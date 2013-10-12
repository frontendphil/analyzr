from datetime import datetime

from django.db import models
from django.db.models import Count
from django.db.models.signals import post_save
from django.dispatch import receiver

from timezone_field import TimeZoneField

from mimetypes import guess_type

from parsr.connectors import Connector, Action
from parsr.analyzers import Analyzer
from parsr import sql

from analyzr.settings import TIME_ZONE


class Repo(models.Model):

    TYPES = (
        ("svn", "Subversion"),
        ("git", "Git"),
        ("mercurial", "Mercurial")
    )

    url = models.CharField(max_length=255)
    kind = models.CharField(max_length=255, choices=TYPES)

    anonymous = models.BooleanField(default=True)

    analyzed = models.BooleanField(default=False)
    analyzing = models.BooleanField(default=False)
    analyzed_date = models.DateTimeField(null=True, blank=True)

    measured = models.BooleanField(default=False)
    measuring = models.BooleanField(default=False)

    timezone = TimeZoneField(default=TIME_ZONE)

    user = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return "%s repository at: %s" % (self.kind, self.url)

    def analyze(self, branch):
        self.analyzed = False
        self.analyzing = True
        self.save()

        self.cleanup(branch)

        connector = Connector.get(self)
        connector.analyze(branch)

        self.analyzing = False
        self.analyzed = True
        self.analyzed_date = datetime.now(self.timezone)
        self.save()

    def remove_all(self, cls, elements):
        query = sql.delete(cls, str(elements.values("id").query))

        cls.objects.raw(query)

    def cleanup(self, branch):
        self.remove_all(File, File.objects.filter(revision__repo=self, revision__branch=branch))
        self.remove_all(Revision, Revision.objects.filter(repo=self, branch=branch))
        self.remove_all(Author, Author.objects.filter(repo=self, revision__branch=branch))

    def busy(self):
        return self.analyzing or self.measuring

    def get_status(self):
        if self.analyzing:
            return "Analyzing"

        return "Measuring"

    def measure(self, branch):
        self.measured = False
        self.measuring = True
        self.save()

        analyzer = Analyzer(self, branch)
        analyzer.start()

        self.measuring = False
        self.measured = True
        self.save()

    def abort_measure(self):
        self.measured = False
        self.measuring = False

        self.save()

    def abort_analyze(self):
        self.analyzed = False
        self.analyzing = False

        self.save()

    def measurable(self):
        for branch in self.branch_set.all():
            if branch.analyzed():
                return True

        return False

    def create_revision(self, branch, identifier):
        return Revision.objects.create(
            repo=self,
            branch=branch,
            identifier=identifier
        )

    def branch_count(self):
        return self.branch_set.count()

    def author_count(self):
        return self.author_set.count()

    def default_branch(self):
        default = Branch.objects.filter(repo=self)[0:1]

        if default:
            return default[0]

        return None

    def age(self):
        if not self.analyzed or self.revision_set.count() == 0:
            return "n/a"

        start = self.revision_set.order_by("revision_date__date")[0:1][0]
        end = self.revision_set.order_by("-revision_date__date")[0:1][0]

        return end.date() - start.date()

    def authors(self, branch):
        return Author.objects.filter(repo=self, revision__branch=branch)\
                             .annotate(revision_count=Count("revision"))\
                             .order_by("-revision_count")

    def revisions(self):
        return Revision.objects.filter(repo=self)\
                               .order_by("revision_date__date")

    def file_statistics(self, branch, author=None):
        result = []

        files = File.objects.filter(revision__repo=self, revision__branch=branch, mimetype__isnull=False)

        if author:
            files = files.filter(revision__author=author)

            count = files.values("mimetype").count()

            for stat in files.values("mimetype").annotate(count=Count("mimetype")).order_by("-count"):
                result.append({
                    "mimetype": stat["mimetype"],
                    "share": stat["count"] / (1.0 * count)
                })

            return result

        query = sql.newest_files(str(files.query))
        count = File.objects.raw(sql.count_entries(query))[0].count

        # Order by
        for stat in File.objects.raw(sql.mimetype_count(query)):
            result.append({
                "mimetype": stat.mimetype,
                "share": stat.count / (1.0 * count)
            })

        return result

    def commit_history(self, branch, author=None):
        revisions = Revision.objects.filter(repo=self, branch=branch)

        if author:
            revisions = revisions.filter(author=author)

        response = {
            "data": {}
        }

        result = revisions.values("revision_date__year", "revision_date__month", "revision_date__day")\
                          .annotate(count=Count("revision_date__day"))

        count_max = 0

        for revision in result:
            count_max = max(revision["count"], count_max)

            year = revision["revision_date__year"]
            month = revision["revision_date__month"]
            day = revision["revision_date__day"]
            count = revision["count"]

            if not year in response["data"]:
                response["data"][year] = {}

            if not month in response["data"][year]:
                response["data"][year][month] = {}

            response["data"][year][month][day] = count

        response["upper"] = count_max

        return response

    def punchcard(self, branch, author=None):
        revisions = Revision.objects.filter(repo=self, branch=branch)

        if author:
            revisions = revisions.filter(author=author)

        response = {}

        result = revisions.values("revision_date__weekday", "revision_date__hour")\
                          .annotate(count=Count("revision_date__hour"))

        hour_max = 0

        for revision in result:
            weekday = revision["revision_date__weekday"]
            hour = revision["revision_date__hour"]
            count = revision["count"]

            hour_max = max(count, hour_max)

            if not weekday in response:
                response[weekday] = {}

            response[weekday][hour] = count

        response["max"] = hour_max

        return response


@receiver(post_save, sender=Repo)
def add_branches_to_repo(sender, **kwargs):
    instance = kwargs["instance"]

    if instance.branch_set.count() > 0:
        return

    connector = Connector.get(instance)

    for name, path in connector.get_branches():
        branch, created = Branch.objects.get_or_create(
            name=name,
            path=path,
            repo=instance
        )


class Branch(models.Model):

    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)

    repo = models.ForeignKey("Repo", null=True)

    def __unicode__(self):
        return "Branch %s at %s" % (self.name, self.path)

    def analyzed(self):
        return Revision.objects.filter(branch=self).count() > 0

class Revision(models.Model):

    identifier = models.CharField(max_length=255)

    repo = models.ForeignKey("Repo")
    branch = models.ForeignKey("Branch", null=True)
    author = models.ForeignKey("Author", null=True, blank=True)
    revision_date = models.ForeignKey("RevisionDate", null=True, blank=True)

    def __unicode__(self):
        return "%s created by %s in %s" % (self.identifier, self.author, self.repo)

    def add_file(self, filename, action, original=None):
        mimetype, encoding = guess_type(filename)

        if original:
            original = File.objects\
                           .filter(name=original, revision__repo=self.repo)\
                           .order_by("-revision__revision_date__date")[0:1]

        File.objects.get_or_create(
            revision=self,
            name=filename,
            mimetype=mimetype,
            change_type=action,
            copy_of=original[0] if original else None
        )

    def set_author(self, name):
        author, created = Author.objects.get_or_create(
            repo=self.repo,
            name=name
        )

        self.author = author

    def set_date(self, date):
        self.revision_date = RevisionDate.from_date(date, self.repo.timezone)

    def date(self):
        return self.revision_date.date

    def modified_files(self):
        return self.file_set.filter(change_type__in=[Action.ADD, Action.MODIFY])


class RevisionDate(models.Model):

    date = models.DateTimeField()

    year = models.IntegerField()
    month = models.IntegerField()
    day = models.IntegerField()
    hour = models.IntegerField()
    minute = models.IntegerField()

    weekday = models.IntegerField()

    @classmethod
    def normalize(cls, date, tzinfo):
        return datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=date.hour,
            minute=date.minute,
            tzinfo=tzinfo
        )

    @classmethod
    def from_date(cls, date, tzinfo):
        date = cls.normalize(date, tzinfo)

        revision_date, created = cls.objects.get_or_create(
            date=date,
            year=date.year,
            month=date.month,
            day=date.day,
            weekday=date.weekday(),
            hour=date.hour,
            minute=date.minute
        )

        return revision_date

    def __unicode__(self):
        return self.date.strftime("%d/%m/%Y - %H:%M")


class File(models.Model):

    CHANGE_TYPES = (
        (Action.ADD, "Added"),
        (Action.MODIFY, "Modified"),
        (Action.MOVE, "Copied"),
        (Action.DELETE, "Deleted")
    )

    revision = models.ForeignKey("Revision")

    name = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255, null=True)

    change_type = models.CharField(max_length=1, null=True, choices=CHANGE_TYPES)
    copy_of = models.ForeignKey("File", null=True)

    def __unicode__(self):
        return self.name


class Author(models.Model):

    repo = models.ForeignKey("Repo", null=True, blank=True)

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def revision_count(self):
        return Revision.objects.filter(author=self, repo=self.repo).count()

    def json(self):
        return {
            "id": self.id,
            "name": self.name,
            "count": self.revision_count
        }
