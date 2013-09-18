from datetime import datetime

from django.db import models
from django.db.models import Count, Sum
from django.db.models.signals import post_save
from django.dispatch import receiver

from timezone_field import TimeZoneField

from parsr.connectors import Connector

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

    timezone = TimeZoneField(default=TIME_ZONE)

    user = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return "%s repository at: %s" % (self.kind, self.url)

    def analyze(self, branch):
        self.analyzed = False
        self.analyzing = True
        self.save()

        self.cleanup()

        connector = Connector.get(self)
        connector.analyze(branch)
        connector.get_file_statistics()

        self.analyzing = False
        self.analyzed = True
        self.analyzed_date = datetime.now(self.timezone)
        self.save()

    def cleanup(self):
        FileInfo.objects.filter(repo=self).delete()

    def abort_analyze(self):
        self.analyzed = False
        self.analyzing = False

        self.save()

    def create_revision(self, identifier, filename):
        revision, created = Revision.objects.get_or_create(
            repo=self,
            identifier=identifier
        )

        revision.add_file(filename)

        return revision

    def revision_count(self):
        return self.revision_set.count()

    def author_count(self):
        return self.author_set.count()

    def age(self):
        if not self.analyzed or self.revision_set.count() == 0:
            return "n/a"

        start = self.revision_set.order_by("revision_date__date")[0:1][0]
        end = self.revision_set.order_by("-revision_date__date")[0:1][0]

        return end.date() - start.date()

    def authors(self):
        authors = Author.objects.filter(repo=self)

        return sorted(authors, key=lambda author: author.revision_count())[::-1]

    def add_mime_info(self, mimetype=None):
        if not mimetype or not FileInfo.is_valid(mimetype):
            return

        info, created = FileInfo.objects.get_or_create(repo=self, mimetype=mimetype)
        info.count = info.count + 1
        info.save()

    def file_statistics(self, author=None):
        result = []

        count = FileInfo.objects.filter(repo=self).aggregate(sum=Sum("count"))["sum"] * 1.0

        for stat in FileInfo.objects.filter(repo=self):
            result.append({
                "mimetype": stat.mimetype,
                "share": stat.count / count
            })

        return result

    def commit_history(self, author=None):
        revisions = Revision.objects.filter(repo=self)

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

    def punchcard(self, author=None):
        revisions = Revision.objects.filter(repo=self)

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

    connector = Connector.get(instance)

    for name, path in connector.get_branches():
        branch, created = Branch.objects.get_or_create(
            name=name,
            path=path,
            repo=instance
        )


class FileInfo(models.Model):

    @classmethod
    def is_valid(cls, mimetype):
        if "audio" in mimetype:
            return False

        if "font" in mimetype:
            return False

        if mimetype.startswith("text/") or mimetype.startswith("application/"):
            return True

        if mimetype == "other/other":
            return True

        return False

    mimetype = models.CharField(max_length=50)
    count = models.IntegerField(default=0)

    repo = models.ForeignKey("Repo")


class Branch(models.Model):

    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)

    repo = models.ForeignKey("Repo", null=True)


    def __unicode__(self):
        return "Branch %s at %s" % (self.name, self.path)

class Revision(models.Model):

    identifier = models.CharField(max_length=255)

    repo = models.ForeignKey("Repo")
    author = models.ForeignKey("Author", null=True, blank=True)
    revision_date = models.ForeignKey("RevisionDate", null=True, blank=True)

    def __unicode__(self):
        return "%s created by %s in %s" % (self.identifier, self.author, self.repo)

    def add_file(self, filename):
        File.objects.get_or_create(revision=self, name=filename)

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


class File(models.Model):

    revision = models.ForeignKey("Revision")

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name


class Author(models.Model):

    repo = models.ForeignKey("Repo", null=True, blank=True)

    name = models.CharField(max_length=255)

    def __unicode__(self):
        return self.name

    def revision_count(self):
        return Revision.objects.filter(author=self, repo=self.repo).count()
