from datetime import datetime
from hashlib import md5
from urllib import urlencode

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

    timezone = TimeZoneField(default=TIME_ZONE)

    user = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return "%s repository at: %s" % (self.kind, self.url)

    def busy(self):
        return self.analyzing() or self.measuring()

    def analyzing(self):
        return Branch.objects.filter(repo=self, analyzing=True).count() > 0

    def analyzed(self):
        return Branch.objects.filter(repo=self, analyzed=True).count() > 0

    def measuring(self):
        return Branch.objects.filter(repo=self, measuring=True).count() > 0

    def measurable(self):
        return Branch.objects.filter(repo=self, analyzed=True).count() > 0

    def get_status(self):
        if self.analyzing():
            branch = Branch.objects.get(repo=self, analyzing=True)

            return "Analyzing %s" % branch.name

        if self.measuring():
            branch = Branch.objects.get(repo=self, measuring=True)

            return "Measuring %s" % branch.name

        return "Ready"

    def branch_count(self):
        return Branch.objects.filter(repo=self).count()

    def author_count(self):
        return Author.objects.filter(revision__branch__repo=self).distinct().count()

    def default_branch(self):
        default = Branch.objects.filter(repo=self)[0:1]

        if default:
            return default[0]

        return None


@receiver(post_save, sender=Repo)
def add_branches_to_repo(sender, **kwargs):
    instance = kwargs["instance"]

    if instance.branch_count() > 0:
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

    analyzed = models.BooleanField(default=False)
    analyzing = models.BooleanField(default=False)
    analyzed_date = models.DateTimeField(null=True, blank=True)

    measured = models.BooleanField(default=False)
    measuring = models.BooleanField(default=False)

    def __unicode__(self):
        return "Branch %s at %s" % (self.name, self.path)

    def cleanup(self):
        self.remove_all(File, File.objects.filter(revision__branch=self))
        self.remove_all(Revision, Revision.objects.filter(branch=self))
        self.remove_all(Author, Author.objects.filter(revision__branch=self))

    def remove_all(self, cls, elements):
        query = sql.delete(cls, str(elements.values("id").query))

        sql.execute(query)

    def analyze(self):
        self.analyzed = False
        self.analyzing = True
        self.save()

        self.cleanup()

        connector = Connector.get(self.repo)
        connector.analyze(self)

        self.analyzing = False
        self.analyzed = True
        self.analyzed_date = datetime.now(self.repo.timezone)
        self.save()

    def abort_analyze(self):
        self.analyzed = False
        self.analyzing = False

        self.save()

    def measure(self):
        self.measured = False
        self.measuring = True
        self.save()

        analyzer = Analyzer(self.repo, self)
        analyzer.start()

        self.measuring = False
        self.measured = True
        self.save()

    def abort_measure(self):
        self.measured = False
        self.measuring = False

        self.save()

    def age(self):
        if not self.analyzed or self.revision_set.count() == 0:
            return "n/a"

        start = self.revision_set.order_by("revision_date__date")[0:1][0]
        end = self.revision_set.order_by("-revision_date__date")[0:1][0]

        return end.date() - start.date()

    def punchcard(self, author=None):
        revisions = Revision.objects.filter(branch=self)

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

    def file_statistics(self, author=None):
        result = []

        files = File.objects.filter(revision__branch=self, mimetype__in=Analyzer.parseable_types())

        if author:
            # Author specific stats need to consider all files and changes to them
            # but not deletes
            files = files.filter(revision__author=author, change_type__in=[Action.ADD, Action.MODIFY, Action.MOVE])

            count = files.values("mimetype").count()

            for stat in files.values("mimetype").annotate(count=Count("mimetype")).order_by("count"):
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

    def commit_history(self, author=None):
        revisions = Revision.objects.filter(branch=self)

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

            response["data"][year][month][day] = {
                "commits": count
                # "files": File.objects.filter(revision__revision_date__day=day,
                #                              revision__revision_date__month=month,
                #                              revision__revision_date__year=year,
                #                              revision__branch=self).count()
            }

        response["upper"] = count_max

        return response

    def authors(self):
        return Author.objects.filter(revision__branch=self)\
                             .annotate(rev_count=Count("revision"))\
                             .order_by("-rev_count")

    def author_count(self):
        return Author.objects.filter(revision__branch=self).distinct().count()

    def revisions(self):
        return Revision.objects.filter(branch=self).order_by("revision_date__date")

    def create_revision(self, identifier):
        return Revision.objects.create(
            branch=self,
            identifier=identifier
        )


class Revision(models.Model):

    identifier = models.CharField(max_length=255)

    branch = models.ForeignKey("Branch", null=True)
    author = models.ForeignKey("Author", null=True, blank=True)
    revision_date = models.ForeignKey("RevisionDate", null=True, blank=True)

    next = models.ForeignKey("Revision", related_name='previous', null=True)

    def __unicode__(self):
        return "%s created by %s in branch %s of %s" % (self.identifier, self.author, self.branch, self.branch.repo)

    def add_file(self, filename, action, original=None):
        mimetype, encoding = guess_type(filename)

        if original:
            original = File.objects\
                           .filter(name=original, revision__branch=self.branch)\
                           .order_by("-revision__revision_date__date")[0:1]

        File.objects.create(
            revision=self,
            name=filename,
            mimetype=mimetype,
            change_type=action,
            copy_of=original[0] if original else None
        )

    def set_author(self, name, email=None):
        author, created = Author.objects.get_or_create(
            name=name,
            email=email
        )

        self.author = author

    def set_date(self, date):
        self.revision_date = RevisionDate.from_date(date, self.branch.repo.timezone)

    def date(self):
        return self.revision_date.date

    def modified_files(self):
        return self.file_set.filter(change_type__in=[Action.ADD, Action.MODIFY, Action.MOVE])

    def get_file(self, filename):
        return self.file_set.get(name=filename)


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

    cyclomatic_complexity = models.IntegerField(default=0)
    cyclomatic_complexity_delta = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    def get_previous(self):
        if self.change_type == Action.ADD:
            return None

        try:
            return File.objects.filter(name=self.name,
                                       revision__revision_date__date__lt=self.revision.date())\
                               .order_by("-revision__revision_date__date")[0]
        except:
            files = File.objects.filter(name=self.name,
                                        revision__revision_date__date__lte=self.revision.date())\
                                .order_by("-revision__revision_date__date")

            if files.count() > 1:
                # multiple edits in one minute. we pick something.
                # hopefully does not happen too often
                return files[1]

            return None

    def add_measures(self, measures):
        previous = self.get_previous()

        for measure in measures:
            if measure["kind"] == "CyclomaticComplexity":
                self.cyclomatic_complexity = measure["value"]

                if previous:
                    self.cyclomatic_complexity_delta = measure["value"] - previous.cyclomatic_complexity

        self.save()


class Author(models.Model):

    name = models.CharField(max_length=255)
    email = models.EmailField(null=True)

    def __unicode__(self):
        if self.email:
            return "%s (%s)" % (self.name, self.email)

        return self.name

    def revision_count(self, branch):
        revisions = Revision.objects.filter(author=self, branch=branch).distinct()

        return revisions.count()

    def get_icon(self):
        size = 40
        mail = ""

        if self.email:
            mail = md5(self.email.lower()).hexdigest()

        params = urlencode({
            's': str(size)
        })

        return "http://www.gravatar.com/avatar/%s?%s" % (mail, params)

    def json(self, branch):
        return {
            "id": self.id,
            "name": str(self),
            "icon": self.get_icon(),
            "count": self.revision_count(branch)
        }
