from datetime import datetime
from hashlib import md5
from urllib import urlencode

from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Count, Sum
from django.db.models.signals import post_save, pre_save
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

    ignored_folders = models.CharField(max_length=255, null=True, blank=True)
    ignored_files = models.CharField(max_length=255, null=True, blank=True)

    user = models.CharField(max_length=255, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)

    def __unicode__(self):
        return "%s repository at: %s" % (self.kind, self.url)

    def href(self):
        return reverse("parsr.views.repo", kwargs={"repo_id": self.id})

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

    def measured(self):
        return Branch.objects.filter(repo=self, measured=True).count() > 0

    def get_status(self):
        branch = None
        status = "ready"

        if self.analyzing():
            branch = Branch.objects.get(repo=self, analyzing=True)

            status = "analyzing"

        if self.measuring():
            branch = Branch.objects.get(repo=self, measuring=True)

            status = "measuring"

        return {
            "action": status,
            "rep": branch.json() if branch else None
        }

    def branches(self):
        return Branch.objects.filter(repo=self)

    def branch_count(self):
        return Branch.objects.filter(repo=self).count()

    def author_count(self):
        return Author.objects.filter(revision__branch__repo=self).distinct().count()

    def default_branch(self):
        default = Branch.objects.filter(repo=self, analyzed=True)[0:1]

        if default:
            return default[0]

        return None

    def ignores(self, package, filename):
        if not package.startswith("/"):
            package = "/%s" % package

        if not package.endswith("/"):
            package = "%s/" % package

        for pkg in self.ignored_folders.split(","):
            if pkg and pkg in package:
                return True

        for name in self.ignored_files.split(","):
            if name and filename.startswith(name):
                return True

        return False

    def json(self):
        return {
            "href": self.href(),
            "name": self.url,
            "kind": self.kind,
            "busy": self.busy(),
            "status": self.get_status(),
            "anonymous": self.anonymous,
            "analyzed": self.analyzed(),
            "analyzing": self.analyzing(),
            "measurable": self.measurable(),
            "measured": self.measured(),
            "measuring": self.measuring(),
            "branchCount": self.branch_count(),
            "authorCount": self.author_count(),
            "branches": [branch.json() for branch in self.branch_set.all()]
        }


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


@receiver(pre_save, sender=Repo)
def clean_ignores(sender, instance, **kwargs):
    filenames = []
    foldernames = []

    if instance.ignored_files:
        for filename in instance.ignored_files.split(","):
            filenames.append(filename.strip())

    instance.ignored_files = ",".join(filenames)

    if instance.ignored_folders:
        for foldername in instance.ignored_folders.split(","):
            if not foldername.startswith("/"):
                foldername = "/%s" % foldername

            if not foldername.endswith("/"):
                foldername = "%s/" % foldername

            foldernames.append(foldername)

    instance.ignored_folders = ",".join(foldernames)


class Branch(models.Model):

    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)

    repo = models.ForeignKey("Repo", null=True)

    analyzed = models.BooleanField(default=False)
    analyzing = models.BooleanField(default=False)
    analyzed_date = models.DateTimeField(null=True, blank=True)

    measured = models.BooleanField(default=False)
    measuring = models.BooleanField(default=False)

    revision_count = models.IntegerField(default=0)

    def __unicode__(self):
        return "Branch %s at %s" % (self.name, self.path)

    def json(self):
        info = {}

        if self.analyzing:
            info["action"] = "analyzing"
            info["count"] = self.revision_count,
            info["progress"] = self.revision_set.all().count()

        if self.measuring:
            info["action"] = "measuring"
            info["progress"] = self.revision_set.filter(measured=True).count()
            info["count"] = self.revision_set.all().count()

        return {
            "href": self.href(),
            "name": self.name,
            "path": self.path,
            "analyzed": self.analyzed,
            "analyzing": self.analyzing,
            "measured": self.measured,
            "measuring": self.measuring,
            "activity": info
        }

    def href(self):
        return reverse("parsr.views.branch", kwargs={"branch_id": self.id})

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

        self.measured = False
        self.measuring = False
        self.save()

        self.cleanup()

        connector = Connector.get(self.repo)
        connector.analyze(self)

        # Maybe search and delete empty revisions

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

        sql.reset(self)

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

        files = File.objects.filter(revision__branch=self)

        if author:
            # Author specific stats need to consider all files and changes to them
            # but not deletes
            files = files.filter(mimetype__in=Analyzer.parseable_types())
            files = files.filter(revision__author=author, change_type__in=[Action.ADD, Action.MODIFY, Action.MOVE])

            count = files.values("mimetype").count()

            for stat in files.values("mimetype").annotate(count=Count("mimetype")).order_by("count"):
                result.append({
                    "mimetype": stat["mimetype"],
                    "share": stat["count"] / (1.0 * count)
                })

            return result

        # raw query processing seems to work a little different. that is why we need to
        # manually put the strings into quotes.
        files = files.filter(mimetype__in=["'%s'" % t for t in Analyzer.parseable_types()])

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

    def revisions(self, author=None):
        revisions = Revision.objects.filter(branch=self)

        if author:
            revisions = revisions.filter(author=author)

        return revisions.order_by("revision_date__date")

    def create_revision(self, identifier):
        return Revision.objects.create(
            branch=self,
            identifier=identifier
        )

    def metrics(self, author):
        result = {
            "info": {
                "dates": []
            },
            "data": {}
        }

        for revision in self.revisions(author):
            files = File.objects.filter(
                revision=revision,
                mimetype__in=Analyzer.parseable_types(),
                change_type__in=Action.readable())

            if not files:
                continue

            result["info"]["dates"].append(revision.date().isoformat())

            for f in files:
                if not f.full_path() in result["data"]:
                    result["data"][f.full_path()] = []

                result["data"][f.full_path()].append({
                    "date": revision.date().isoformat(),
                    "deleted": f.change_type == Action.DELETE,
                    "Cyclomatic Complexity": float(f.cyclomatic_complexity),
                    "Halstead Volume": float(f.halstead_volume),
                    "Halstead Difficulty": float(f.halstead_difficulty),
                    "Halstead Effort": float(f.halstead_effort)
                })

        return result

    def churn(self, author):
        result = {
            "info": {
                "dates": []
            },
            "data": []
        }

        for revision in self.revisions(author):
            files = File.objects.filter(revision=revision, mimetype__in=Analyzer.parseable_types())\
                                .aggregate(
                                    added=Sum("lines_added"),
                                    removed=Sum("lines_removed")
                                )

            if not files["added"]:
                # code churn not measured for this revision
                continue

            result["info"]["dates"].append(revision.date().isoformat())

            result["data"].append({
                "date": revision.date().isoformat(),
                "added": files["added"],
                "removed": files["removed"]
            })

        return result

class Revision(models.Model):

    identifier = models.CharField(max_length=255)

    branch = models.ForeignKey("Branch", null=True)
    author = models.ForeignKey("Author", null=True)
    revision_date = models.ForeignKey("RevisionDate", null=True)

    next = models.ForeignKey("Revision", related_name='previous', null=True)

    measured = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s created by %s in branch %s of %s" % (self.identifier, self.author, self.branch, self.branch.repo)

    def add_file(self, filename, action, original=None):
        package, filename = File.parse_name(filename)

        if self.branch.repo.ignores(package, filename):
            return

        mimetype, encoding = guess_type(filename)

        if original:
            original = File.objects\
                           .filter(name=filename, package=package, revision__branch=self.branch)\
                           .order_by("-revision__revision_date__date")[0:1]

        File.objects.create(
            revision=self,
            name=filename,
            package=package,
            mimetype=mimetype.split("/")[1] if mimetype else None,
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

    def get_previous(self):
        if self.previous.all().count() > 0:
            return self.previous.all()[0]

        return None

    def modified_files(self):
        return self.file_set.filter(change_type__in=[Action.ADD, Action.MODIFY, Action.MOVE])

    def includes(self, filename):
        package, filename = File.parse_name(filename)

        return not self.file_set.filter(name=filename, package__endswith=package).count() == 0

    def get_file(self, filename):
        package, filename = File.parse_name(filename)

        return self.file_set.get(name=filename, package__endswith=package, change_type__in=Action.readable())


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

    @classmethod
    def parse_name(cls, filename):
        parts = filename.rsplit("/", 1)

        if not len(parts) == 2:
            parts = [""] + parts

        return parts

    CHANGE_TYPES = (
        (Action.ADD, "Added"),
        (Action.MODIFY, "Modified"),
        (Action.MOVE, "Copied"),
        (Action.DELETE, "Deleted")
    )

    KNOWN_LANGUAGES = Analyzer.parseable_types() + [
        "x-python",
        "html",
        "json",
        "x-sql"
    ]

    revision = models.ForeignKey("Revision")

    name = models.CharField(max_length=255)
    package = models.CharField(max_length=255)

    mimetype = models.CharField(max_length=255, null=True)

    change_type = models.CharField(max_length=1, null=True, choices=CHANGE_TYPES)
    copy_of = models.ForeignKey("File", null=True)

    cyclomatic_complexity = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cyclomatic_complexity_delta = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    halstead_volume = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    halstead_volume_delta = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    halstead_difficulty = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    halstead_difficulty_delta = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    halstead_effort = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    halstead_effort_delta = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    lines_added = models.IntegerField(default=0)
    lines_removed = models.IntegerField(default=0)

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

            if measure["kind"] == "Halstead":
                volume = measure["value"]["volume"]
                difficulty = measure["value"]["difficulty"]
                effort = measure["value"]["effort"]

                self.halstead_volume = volume
                self.halstead_difficulty = difficulty
                self.halstead_effort = effort

                if previous:
                    self.halstead_volume_delta = volume - previous.halstead_volume
                    self.halstead_difficulty_delta = difficulty - previous.halstead_difficulty
                    self.halstead_effort_delta = effort - previous.halstead_effort

            if measure["kind"] == "churn":
                self.lines_added = measure["value"]["added"]
                self.lines_removed = measure["value"]["removed"]

        self.save()

    def add_churn(self, churn=None):
        if not churn:
            return

        self.lines_added = churn["added"]
        self.lines_removed = churn["removed"]

        self.save()

    def get_identifier(self):
        return md5(self.name).hexdigest()

    def full_path(self):
        return "%s/%s" % (self.package, self.name)


class Author(models.Model):

    name = models.CharField(max_length=255)
    email = models.EmailField(null=True)

    def __unicode__(self):
        if self.email:
            return "%s (%s)" % (self.name, self.email)

        return self.name

    def href(self):
        return reverse("parsr.views.author", kwargs={"author_id": self.id})

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

    def get_prime_language(self, branch):
        files = File.objects.filter(
                                revision__branch=branch,
                                revision__author=self,
                                mimetype__in=File.KNOWN_LANGUAGES
                            )\
                            .values("mimetype")\
                            .annotate(count=Count("mimetype"))\
                            .order_by("-count")

        if not files:
            return None

        return files[0]

    def json(self, branch):
        return {
            "href": self.href(),
            "name": str(self),
            "icon": self.get_icon(),
            "count": self.revision_count(branch),
            "primeLanguage": self.get_prime_language(branch)
        }
