import numpy

from datetime import datetime, timedelta
from dateutil import parser
from hashlib import md5
from urllib import urlencode
from fractions import Fraction
from copy import copy

from django.db import models
from django.db.models import Count, Sum, Avg, Min, Max, Q
from django.db.models.signals import post_save, pre_save, pre_delete
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.dispatch import receiver

from timezone_field import TimeZoneField

from mimetypes import guess_type

from parsr.connectors import Connector, Action, ConnectionError
from parsr.analyzers import Analyzer
from parsr.classification import Classify
from parsr import sql, utils

from analyzr.settings import TIME_ZONE, CONTRIBUTORS_PER_PAGE, ANONYMIZE


# in days
IMPACT_TIME_PERIOD = 62


def system_busy():
    return Branch.objects.filter(Q(analyzing=True) | Q(measuring=True)).count() > 0


class Repo(models.Model):
    """
    Repository, BITCH!
    """

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
        return "%s (%s)" % (self.url, self.kind)

    def purge(self):
        try:
            connector = Connector.get(self)
            connector.clear()
        except ConnectionError:
            pass

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
        return Author.objects.filter(revisions__branch__repo=self).distinct().count()

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

    def is_checked_out(self):
        connector = Connector.get(self)

        return connector.is_checked_out()

    def json(self):
        error = None

        checked_out = False

        try:
            checked_out = self.is_checked_out()
        except ConnectionError, e:
            error = e

        return {
            "id": self.id,
            "name": self.url,
            "kind": self.kind,
            "busy": self.busy(),
            "checkedOut": checked_out,
            "status": self.get_status(),
            "anonymous": self.anonymous,
            "analyzed": self.analyzed(),
            "analyzing": self.analyzing(),
            "measurable": self.measurable(),
            "measured": self.measured(),
            "measuring": self.measuring(),
            "branchCount": self.branch_count(),
            "authorCount": self.author_count(),
            "branchIds": [int(value) for value in self.branches.values_list("id", flat=True).distinct()],
            "error": str(error) if error else None
        }


@receiver(post_save, sender=Repo)
def add_branches_to_repo(sender, **kwargs):
    instance = kwargs["instance"]

    if instance.branch_count() > 0:
        return

    try:
        connector = Connector.get(instance)
    except ConnectionError:
        return

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
                foldername = "/%s" % foldername.strip()

            if not foldername.endswith("/"):
                foldername = "%s/" % foldername.strip()

            foldernames.append(foldername)

    instance.ignored_folders = ",".join(foldernames)


@receiver(pre_delete, sender=Repo)
def remove_repo(sender, instance, **kwargs):
    instance.purge()


class Branch(models.Model):

    name = models.CharField(max_length=255)
    path = models.CharField(max_length=255)

    repo = models.ForeignKey("Repo", related_name="branches", null=True)

    analyzed = models.BooleanField(default=False)
    analyzing = models.BooleanField(default=False)
    analyzed_date = models.DateTimeField(null=True, blank=True)

    measured = models.BooleanField(default=False)
    measuring = models.BooleanField(default=False)
    measured_date = models.DateTimeField(null=True, blank=True)

    revision_count = models.IntegerField(default=0)
    last_analyze_error = models.TextField(null=True, blank=True)
    last_measure_error = models.TextField(null=True, blank=True)

    def __unicode__(self):
        return "%s at %s" % (self.name, self.path)

    def json(self, short=False):
        base = {
            "id": self.id,
            "name": self.name,
            "path": self.path,
            "repositoryId": self.repo_id,
            "activity": self.get_info(),
            "analyze": self.get_analyze_state(),
            "measure": self.get_measure_state()
        }

        if not short and self.analyzed:
            base.update({
                "age": str(self.age()),
                "authorCount": self.author_count(),
                "authorRatio": self.author_ratio()
            })

        return base

    def get_measure_state(self):
        return {
            "date": self.measured_date.isoformat() if self.measured_date else None,
            "running": self.measuring,
            "finished": self.measured,
            "interrupted": self.measuring_interrupted(),
            "lastError": self.last_measure_error
        }

    def get_analyze_state(self):
        return {
            "date": self.analyzed_date.isoformat() if self.analyzed_date else None,
            "running": self.analyzing,
            "finished": self.analyzed,
            "interrupted": self.analyzing_interrupted(),
            "lastError": self.last_analyze_error
        }

    def get_info(self):
        if self.analyzing:
            return {
                "action": "analyzing",
                "count": self.revision_count,
                "progress": self.revisions.all().count()
            }

        if self.measuring:
            return {
                "action": "measuring",
                "progress": self.revisions.filter(measured=True).count(),
                "count": self.revisions.all().count()
            }

        return {}

    def work_force(self):
        force = []

        for author in self.authors():
            force.append((author, author.classify(self)))

        return force

    def analyzing_interrupted(self):
        return not self.analyzed and self.revisions.count() > 0

    def measuring_interrupted(self):
        measured = self.revisions.filter(measured=True).count()

        return measured > 0 and not measured == self.revisions.all().count()

    def cleanup(self):
        self.remove_all(Revision, Revision.objects.filter(branch=self))
        self.remove_all(File, File.objects.filter(revision__branch=self))
        self.remove_all(Author, Author.objects.filter(revisions__branch=self))

        # ForeignKey constraints ensure that all packages re being deleted
        root = Package.root(self)
        if root:
            root.delete()

    def remove_all(self, cls, elements):
        query = sql.delete(cls, str(elements.values("id").query))

        sql.execute(query)

    def analyze(self, resume=False):
        if system_busy():
            return

        self.last_analyze_error = None

        self.analyzed = False
        self.analyzing = True

        self.measured = False
        self.measuring = False
        self.save()

        if not resume:
            self.cleanup()

        revision = None

        self.create_root_package()

        if resume:
            revision = self.last_analyzed_revision()

        connector = Connector.get(self.repo)
        connector.analyze(self, revision)

        self.init_packages()

        self.analyzing = False
        self.analyzed = True
        self.analyzed_date = datetime.now(self.repo.timezone)
        self.save()

    def abort_analyze(self, error):
        self.analyzed = False
        self.analyzing = False

        self.last_analyze_error = error

        self.save()

    def create_root_package(self):
        Package.objects.get_or_create(parent=None, branch=self, name="/")

    def init_packages(self):
        root = Package.root(self)
        root.update()

    def last_analyzed_revision(self):
        return self.revisions.get(previous=None)

    def last_measured_revision(self):
        revisions = self.revisions.filter(measured=True).order_by("-date")

        if revisions.count() == 0:
            return None

        return revisions[0]

    def measure(self, resume=False):
        if system_busy():
            return

        self.last_measure_error = None

        self.measured = False
        self.measuring = True
        self.save()

        if not resume:
            sql.reset(self)

        revision = None

        if resume:
            revision = self.last_measured_revision()

        analyzer = Analyzer(self.repo, self)
        analyzer.start(revision)

        self.measuring = False
        self.measured = True
        self.measured_date = datetime.now(self.repo.timezone)
        self.save()

    def abort_measure(self, error):
        self.measured = False
        self.measuring = False

        self.last_measure_error = error

        self.save()

    def age(self):
        if not self.analyzed or self.revisions.count() == 0:
            return "n/a"

        start = self.revisions.order_by("date")[0:1][0]
        end = self.revisions.order_by("-date")[0:1][0]

        if not end.date or not start.date:
            import pdb; pdb.set_trace()

        return end.date - start.date

    def author_ratio(self):
        # this value might needs to be normalized using the age of the repository
        # because the longer a repository exists, the more devs come and go

        return round(100 * (len(self.main_contributors(active=True)) / (1.0 * self.author_count())), 2)

    def main_contributors(self, active=False):
        revisions = Revision.objects.filter(branch=self)

        if active:
            # active means during the last month since it has been last analyzed
            # using the current date here would make no sense
            revisions = revisions.filter(date__gte=self.analyzed_date - timedelta(days=IMPACT_TIME_PERIOD))

        revision_count = revisions.count()

        authored = revisions.values("author").annotate(count=Count("id"))

        main_contributors = []

        for revision in authored:
            if (100.0 * revision["count"]) / revision_count > 5:
                main_contributors.append(revision)

        # -1 in order to sort descending
        main_contributors = sorted(main_contributors, key=lambda revision: -1 * revision["count"])

        return [(revision["author"], revision["count"]) for revision in main_contributors]

    def impact(self):
        authors = self.main_contributors(active=True)

        response = self.response_stub()

        response["info"]["authorCount"] = len(authors)
        response["data"] = []

        for author_id, count in authors:
            response["data"].append({
                "href": utils.href(Author, author_id),
                "count": count
            })

        return response

    def compute_statistics(self, files, metric):
        file_count = files.count() * 1.0

        increase_filter = {}
        increase_filter["%s_delta__gt" % metric] = 0

        decrease_filter = {}
        decrease_filter["%s_delta__lt" % metric] = 0

        num_increase = files.filter(**increase_filter).count()
        num_decreaes = files.filter(**decrease_filter).count()

        percent_increase = num_increase / file_count
        percent_decrease = num_decreaes / file_count
        percent_unmodified = 1 - percent_increase - percent_decrease

        return {
            "increases": num_increase,
            "decreases": num_decreaes,
            "percent_increase": percent_increase * 100,
            "percent_decrease": percent_decrease * 100,
            "percent_unmodified": percent_unmodified * 100,
            "decreases_to_increase": percent_decrease / percent_increase if percent_increase else 1,
            "unmodified_to_increase": percent_unmodified / percent_increase if percent_increase else 1,
            "unmodified_to_decrease": percent_unmodified / percent_decrease if percent_decrease else 1
        }

    def compute_scores(self, files, metrics):
        kwargs = {}
        aggregations = {
            "sum": Sum,
            "max": Max,
            "min": Min,
            "avg": Avg
        }

        result = {}

        for metric in metrics:
            if not metric in result:
                result[metric] = {}
                result["%s_delta" % metric] = {}

            result[metric]["statistics"] = self.compute_statistics(files, metric)

            for key, value in aggregations.iteritems():
                kwargs["%s_delta_%s" % (metric, key)] = value("%s_delta" % metric)
                kwargs["%s_%s" % (metric, key)] = value(metric)

        aggregate = files.aggregate(**kwargs)

        for key, value in aggregate.iteritems():
            v = float(value)
            key, kind = key.rsplit("_", 1)

            result[key][kind] = v

        return result, aggregations

    def score(self, author=None, language=None):
        result = self.response_stub(language=language)

        files = self.files(author=author, language=language)

        metrics = [
            "cyclomatic_complexity",
            "halstead_difficulty",
            "halstead_volume",
            "fan_in",
            "fan_out",
            "sloc_squale",
            "sloc"
        ]

        aggregate, aggregations = self.compute_scores(files, metrics)

        result["info"]["keys"] = aggregations.keys()
        result["data"] = aggregate

        return result

    def set_options(self, response, options):
        for key, value in options.iteritems():
            response["info"]["options"][key] = value

    def get_package_tree(self, packages, right):
        """
        Parse a hierarchy represented as a nested set back into
        a tree. This is done in one run over the structure.
        """
        children = []

        while packages:
            package = packages[-1]

            if package.left > right:
                return children

            packages.pop()

            node = package.json()
            node["rep"]["children"] = self.get_package_tree(packages, package.right)

            children.append(node)

        return children

    def packages(self):
        packages = list(Package.objects.filter(branch=self).distinct().order_by("-left"))
        root = packages.pop()

        result = root.json()
        result["rep"]["children"] = self.get_package_tree(packages, root.right)

        return result


    def contributors(self, page=None):
        response = self.response_stub()

        authors = self.authors().annotate(rev_count=Count("revisions")).order_by("-rev_count")

        paginator = Paginator(authors, CONTRIBUTORS_PER_PAGE)

        try:
            authors = paginator.page(page)
        except PageNotAnInteger:
            page = 1
            authors = paginator.page(1)
        except EmptyPage:
            page = paginator.num_pages
            authors = paginator.page(paginator.num_pages)

        response["data"] = [author.json(self) for author in authors]

        self.set_options(response, {
            "hasNext": not page == paginator.num_pages,
            "hasPrevious": not page == 1,
            "page": int(page),
            "pages": paginator.num_pages,
            "perPage": CONTRIBUTORS_PER_PAGE
        })

        return response

    def punchcard(self, author=None, language=None, start=None, end=None):
        filters = {
            "branch": self
        }

        if author:
            filters["author"] = author

        response = self.response_stub(language=language, start=start, end=end)

        result = Revision.objects.filter(**filters).values("weekday", "hour").annotate(count=Count("hour"))

        hour_max = 0

        for revision in result:
            weekday = revision["weekday"]
            hour = revision["hour"]
            count = revision["count"]

            hour_max = max(count, hour_max)

            if not weekday in response["data"]:
                response["data"][weekday] = {}

            response["data"][weekday][hour] = count

        self.set_options(response, {
            "max": hour_max
        })

        return response

    def file_statistics(self, author=None):
        response = self.response_stub()
        files = self.files(author=author, escaped=(author is None))

        if author:
            count = files.count()

            for stat in files.values("mimetype").annotate(count=Count("mimetype")).order_by("count"):
                response["data"][stat["mimetype"]] = stat["count"] / (1.0 * count)

            return response

        query = sql.newest_files(str(files.query))
        count = File.objects.raw(sql.count_entries(query))[0].count

        for stat in File.objects.raw(sql.mimetype_count(query)):
            response["data"][stat.mimetype] = stat.count / (1.0 * count)

        return response

    def commit_history(self, author=None, language=None, start=None, end=None):
        filters = {
            "branch": self
        }

        if author:
            filters["author"] = author

        response = self.response_stub()

        result = Revision.objects.filter(**filters).values("year", "month", "day").annotate(count=Count("day"))

        count_max = 0

        for revision in result:
            count_max = max(revision["count"], count_max)

            year = revision["year"]
            month = revision["month"]
            day = revision["day"]
            count = revision["count"]

            if not year in response["data"]:
                response["data"][year] = {}

            if not month in response["data"][year]:
                response["data"][year][month] = {}

            response["data"][year][month][day] = {
                "commits": count,
                "files": File.objects.filter(day=day, month=month, year=year, branch=self).count()
            }

        self.set_options(response, {
            "upper": count_max
        })

        return response

    def authors(self, language=None, raw=False):
        filters = {
            "revisions__branch": self
        }

        if language:
            filters["revisions__files__mimetype"] = "'%s'" % language if raw else language

        return Author.objects.filter(**filters).distinct().order_by("name")

    def author_count(self):
        return self.authors().count()

    def first_revision(self):
        revisions = self.revisions.all().order_by("date")

        if revisions.count() == 0:
            return None

        return revisions[0]

    def revisions(self, author=None, language=None, start=None, end=None):
        filters = {
            "branch": self
        }

        if author:
            filters["author"] = author

        if language == "all":
            # all is a special value for the language attribute
            # which will reset it so that no filtering will take place
            language = None

        if language:
            filters["file__mimetype"] = language

        if start:
            filters["date__gte"] = start

        if end:
            filters["date__lte"] = end

        return Revision.objects.filter(**filters).order_by("date")

    def files(self, author=None, language=None, package=None, start=None, end=None, actions=Action.checkable(), escaped=False):
        filters = {
            "revision__branch": self,
            "faulty": False,
            "change_type__in": ['"%s"' % action for action in actions] if escaped else actions
        }

        if author:
            filters["author"] = author

        if language:
            filters["mimetype"] = '%s' % language if escaped else language

        if start:
            filters["date__gte"] = '%s' % start.strftime("%Y-%m-%d %H:%M:%S") if escaped else start

        if end:
            filters["date__lte"] = '%s' % end.strftime("%Y-%m-%d %H:%M:%S") if escaped else end

        if package:
            filters["pkg__left__gte"] = package.left
            filters["pkg__right__lte"] = package.right

        return File.objects.filter(**filters).distinct().order_by("date")

    def create_revision(self, identifier):
        return Revision.objects.create(
            branch=self,
            identifier=identifier
        )

    def get_languages(self):
        languages = File.objects\
            .filter(revision__branch=self, mimetype__in=Analyzer.parseable_types())\
            .values("mimetype").distinct()

        return [language["mimetype"] for language in languages]

    def get_earliest_revision(self):
        revisions = self.revisions.filter(date__isnull=False).order_by("date")[0:1]

        if not revisions:
            return None

        return revisions[0]

    def get_latest_revision(self):
        revisions = self.revisions.filter(date__isnull=False).order_by("-date")[0:1]

        if not revisions:
            return None

        return revisions[0]

    def response_stub(self, language=None, package=None, start=None, end=None):
        earliest = self.get_earliest_revision()
        latest = self.get_latest_revision()

        return {
            "info": {
                "dates": [],
                "languages": self.get_languages(),
                "options": {
                    "language": language,
                    "package": utils.href(Package, package.id) if package else None,
                    "startDate": start.isoformat() if start else None,
                    "endDate": end.isoformat() if end else None,
                    "minDate": earliest.date.isoformat() if earliest else None,
                    "maxDate": latest.date.isoformat() if latest else None
                }
            },
            "data": {}
        }

    def get_tzinfo(self):
        now = datetime.now()
        tz_abbr = self.repo.timezone.tzname(now)

        tzinfo = {}
        tzinfo[tz_abbr] = self.repo.timezone.zone

        return tzinfo

    def get_average_revisions(self, language=None):
        authors = self.authors(language=language, raw=True)\
                   .distinct()\
                   .values("id")\
                   .annotate(rev_count=Count("revisions"))

        return sql.average(str(authors.query), "rev_count")

    def parse_revision_authors(self, revisions, metrics, language=None):
        data = {}
        dates = []
        authors = {}
        changes = {}

        for revision in revisions:
            author = utils.href(Author, revision["author"])
            date = revision["date"]

            if not date in dates:
                dates.append(date)

            if not author in authors:
                changes[author] = {
                    "increases": 0,
                    "decreases": 0
                }

                authors[author] = {
                    "href": author,
                    "increases": 0,
                    "decreases": 0,
                    "revisions": 0,
                    "loc": 0,
                    "score": 0
                }

            current = authors[author]

            current["revisions"] += 1
            current["loc"] = max(0, current["loc"] + revision["sloc_sum"])

            for metric in metrics:
                if metric == "sloc_sum":
                    continue

                value = revision["%s_sum" % metric]

                if value > 0:
                    changes[author]["increases"] += 1

                if value < 0:
                    changes[author]["decreases"] += 1

            if changes[author]["decreases"]:
                ratio = Fraction(changes[author]["increases"], changes[author]["decreases"])
            else:
                ratio = 1

            current["score"] = ratio * numpy.log(1 + float(current["revisions"]))
            # current["score"] = current["score"] + ratio + numpy.log(1 + float(current["revisions"]))
            # current["score"] = current["score"] + (numpy.log(1 + float(current["loc"])) / average_revisions)

            date = date.isoformat()

            authors[author]["last_active"] = date

            if not date in data:
                data[date] = []

            data[date].append(copy(authors[author]))

        return data, dates

    def clean_active_authors(self, authors, date, tzinfo):
        inactive = []

        for href, stat in authors.iteritems():
            last_active = parser.parse(stat["last_active"], tzinfos=tzinfo)

            if date - last_active > timedelta(days=31):
                inactive.append(href)

        for author in inactive:
            del authors[author]

    def get_top_author(self, authors, rank=False):
        values = authors.values()
        values = sorted(values, key=lambda author: author["score"])
        values = values[::-1]

        if rank:
            return values

        return values[0] if values else None

    def get_current_top_authors(self, language, package=None, start=None, end=None):
        response = self.response_stub(language=language, package=package, start=None, end=None)

        experts = self.experts(language=language, package=package, start=start, end=end, rank=True)

        dates = experts["info"]["dates"]

        response["data"] = []

        if not dates:
            return response

        last_date = dates[-1]

        response["data"] = experts["data"][last_date]

        return response

    def experts(self, rank=False, language=None, package=None, start=None, end=None):
        response = self.response_stub(language=language, package=package, start=start, end=end)

        if not language:
            return response

        metrics = [
            "cyclomatic_complexity",
            "halstead_volume",
            "halstead_difficulty",
            "fan_in",
            "fan_out",
            "sloc_squale",
            "sloc"
        ]

        def get_annotation(metrics):
            annotation = {}

            for metric in metrics:
                annotation["%s_sum" % metric] = Sum("%s_delta" % metric)

            return annotation

        files = self.files(language=language, package=package, start=start, end=end)
        revisions = files.values("revision", "author", "date").order_by("date").annotate(**get_annotation(metrics))

        data, dates = self.parse_revision_authors(revisions, metrics, language=language)

        response["info"]["dates"] = [date.isoformat() for date in dates]
        response["info"]["options"]["startDate"] = dates[0].isoformat() if dates else None
        response["info"]["options"]["endDate"] = dates[-1].isoformat() if dates else None

        tzinfo = self.get_tzinfo()
        active_authors = {}

        for date in dates:
            actions = data[date.isoformat()]

            for action in actions:
                active_authors[action["href"]] = action

            self.clean_active_authors(active_authors, date, tzinfo)

            top_author = self.get_top_author(active_authors, rank=rank)

            if not top_author:
                continue

            if rank:
                for author in top_author:
                    author["score"] = float(author["score"])
            else:
                top_author["score"] = float(top_author["score"])

            response["data"][date.isoformat()] = top_author

        return response

    def aggregated_metrics(self, author=None, language=None, package=None, start=None, end=None):
        result = self.response_stub(language=language, package=package, start=start, end=end)

        if not language:
            return result

        files = self.files(
            author=author,
            language=language,
            package=package,
            start=start,
            end=end
        )

        files = files.values("date", "revision").annotate(
            cyclomatic_complexity=Avg("cyclomatic_complexity"),
            cyclomatic_complexity_delta=Avg("cyclomatic_complexity_delta"),
            halstead_volume=Avg("halstead_volume"),
            halstead_volume_delta=Avg("halstead_volume_delta"),
            halstead_difficulty=Avg("halstead_difficulty"),
            halstead_difficulty_delta=Avg("halstead_difficulty_delta"),
            fan_in=Avg("fan_in"),
            fan_in_delta=Avg("fan_in_delta"),
            fan_out=Avg("fan_out"),
            fan_out_delta=Avg("fan_out_delta"),
            sloc=Sum("sloc"),
            sloc_delta=Sum("sloc_delta")
        )

        result["data"] = []

        value = None

        for rev in files:
            date = rev["date"].isoformat()

            if not date in result["info"]["dates"]:
                result["info"]["dates"].append(date)

            if not value:
                value = {
                    "cyclomatic_complexity": rev["cyclomatic_complexity"],
                    "halstead_difficulty": rev["halstead_difficulty"],
                    "halstead_volume": rev["halstead_volume"],
                    "fan_in": rev["fan_in"],
                    "fan_out": rev["fan_out"],
                    "sloc": rev["sloc"]
                }
            else:
                value["cyclomatic_complexity"] += rev["cyclomatic_complexity_delta"]
                value["halstead_difficulty"] += rev["halstead_difficulty_delta"]
                value["halstead_volume"] += rev["halstead_volume_delta"]
                value["fan_in"] += rev["fan_in_delta"]
                value["fan_out"] += rev["fan_out_delta"]
                value["sloc"] += rev["sloc_delta"]

            result["data"].append({
                "href": "/file/all",
                "rel": "file",
                "rep": {
                    "date": date,
                    "revision": utils.href(Revision, rev["revision"]),
                    "complexity": {
                        "cyclomatic_complexity": value["cyclomatic_complexity"],
                        "cyclomatic_complexity_delta": rev["cyclomatic_complexity_delta"],
                        "halstead_volume": value["halstead_volume"],
                        "halstead_volume_delta": rev["halstead_volume_delta"],
                        "halstead_difficulty": value["halstead_difficulty"],
                        "halstead_difficulty_delta": rev["halstead_difficulty_delta"]
                    },
                    "structure": {
                        "fan_in": value["fan_in"],
                        "fan_in_delta": rev["fan_in_delta"],
                        "fan_out": value["fan_out"],
                        "fan_out_delta": rev["fan_out_delta"],
                        "sloc": value["sloc"],
                        "sloc_delta": rev["sloc_delta"]
                    }
                }
            })

        return result

    def metrics(self, author=None, language=None, package=None, start=None, end=None):
        result = self.response_stub(language=language, package=package, start=start, end=end)

        if not language:
            return result

        files = self.files(author=author, language=language, package=package, start=start, end=end)

        for f in files:
            date = f.date.isoformat()

            if not date in result["info"]["dates"]:
                result["info"]["dates"].append(date)

            path = f.full_path()

            if not path in result["data"]:
                result["data"][path] = []

            last = result["data"][path][-1] if len(result["data"][path]) > 0 else None

            result["data"][path].append(f.json(last["rep"] if last else None))

        result["data"]["all"] = self.aggregated_metrics(
            author=author,
            language=language,
            package=package,
            start=start,
            end=end)["data"]

        return result

    def churn(self, author=None, language=None, package=None, start=None, end=None):
        response = self.response_stub(language=language, package=package, start=start, end=end)

        if not language:
            self.set_options(response, {
                "upperBound": 1,
                "lowerBound": -1
            })

            return response

        max_added = 0
        max_removed = 0

        files = self.files(author=author, actions=Action.readable(), language=language, package=package, start=start, end=end)
        revisions = files.values("date").annotate(added=Sum("lines_added"), removed=Sum("lines_removed"))

        for revision in revisions:
            response["info"]["dates"].append(revision["date"].isoformat())

            max_added = max(max_added, revision["added"])
            max_removed = max(max_removed, revision["removed"])

            response["data"][revision["date"].isoformat()] = {
                "added": revision["added"],
                "removed": revision["removed"]
            }

        self.set_options(response, {
            "startDate": revisions[0]["date"].isoformat(),
            "endDate": revisions[len(revisions) - 1]["date"].isoformat(),
            "upperBound": max_added,
            "lowerBound": -1 * max_removed
        })

        return response

class Revision(models.Model):

    identifier = models.CharField(max_length=255)

    branch = models.ForeignKey("Branch", related_name="revisions", null=True)
    author = models.ForeignKey("Author", related_name="revisions", null=True)
    message = models.TextField(default="")

    next = models.ForeignKey("Revision", related_name='previous', null=True)

    measured = models.BooleanField(default=False)

    date = models.DateTimeField(null=True)

    year = models.IntegerField(null=True)
    month = models.IntegerField(null=True)
    day = models.IntegerField(null=True)
    hour = models.IntegerField(null=True)
    minute = models.IntegerField(null=True)
    weekday = models.IntegerField(null=True)

    def __unicode__(self):
        return "id:\t\t%s\nauthor:\t\t%s\ndate:\t\t%s\nbranch:\t\t%s\nrepository:\t%s" % (
            self.identifier,
            self.author,
            self.date,
            self.branch,
            self.branch.repo
        )

    def json(self):
        return {
            "href": utils.href(Revision, self.id),
            "view": utils.view(Revision, self.id),
            "rel": "revision",
            "rep": {
                "identifier": self.identifier,
                "branch": utils.href(Branch, self.branch_id),
                "author": utils.href(Author, self.author_id),
                "next": utils.href(Revision, self.next_id) if self.next else None,
                "measured": self.measured,
                "message": self.message,
                "date": self.date.isoformat(),
                "files": [f.json() for f in self.files.all()],
                "complexDate": {
                    "year": self.year,
                    "month": self.month,
                    "day": self.day,
                    "hour": self.hour,
                    "minute": self.minute,
                    "weekday": self.weekday
                }
            }
        }

    def add_file(self, filename, action, original=None):
        package, filename = File.parse_name(filename)

        if self.branch.repo.ignores(package, filename):
            return

        mimetype, encoding = guess_type(filename)
        mimetype = mimetype.split("/")[1] if mimetype else None

        # reject all files that wouldn't be measurable anyways.
        if not mimetype in Analyzer.parseable_types():
            return

        if original:
            original = File.objects\
                           .filter(name=filename, package=package, revision__branch=self.branch)\
                           .order_by("-date")[0:1]

        pkg = Package.get(package, self.branch)

        File.objects.create(
            revision=self,
            author=self.author,
            date=self.date,
            name=filename,
            package=pkg.name,
            pkg=pkg,
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

    def normalize_date(self, date, tzinfo):
        return datetime(
            year=date.year,
            month=date.month,
            day=date.day,
            hour=date.hour,
            minute=date.minute,
            tzinfo=tzinfo
        )

    def set_date(self, date):
        date = self.normalize_date(date, self.branch.repo.timezone)

        self.date = date
        self.year = date.year
        self.month = date.month
        self.day = date.day
        self.weekday = date.weekday()
        self.hour = date.hour
        self.minute = date.minute

    def get_previous(self):
        if self.previous.all().count() > 0:
            return self.previous.all()[0]

        return None

    def represents(self, identifier):
        return self.identifier == identifier

    def modified_files(self):
        return self.files.filter(
            change_type__in=Action.readable(),
            mimetype__in=Analyzer.parseable_types()
        )

    def diff(self):
        previous = self.get_previous()

        connector = Connector.get(self.branch.repo)

        return connector.diff(previous, self)

    def includes(self, filename):
        package, filename = File.parse_name(filename)

        return not self.files.filter(name=filename,
                                        package__endswith=package,
                                        change_type__in=Action.readable()).count() == 0

    def get_file(self, filename):
        package, filename = File.parse_name(filename)

        try:
            return self.files.get(name=filename,
                                     package__endswith=package,
                                     change_type__in=Action.readable())
        except File.DoesNotExist:
            message = "Could not find file using package: %s and filename: %s." % (
                package,
                filename
            )

            raise Exception(message)
        except File.MultipleObjectsReturned:
            # This  happens only in very rare cases... Let's hope what we do
            # about it does not harm
            return self.files.filter(name=filename,
                                     package__endswith=package,
                                     change_type__in=Action.readable())[0]

    def stats(self):
        return File.objects.filter(revision=self).aggregate(
            cyclomatic_complexity=Avg("cyclomatic_complexity"),
            cyclomatic_complexity_delta=Avg("cyclomatic_complexity_delta"),
            halstead_volume=Avg("halstead_volume"),
            halstead_volume_delta=Avg("halstead_volume_delta"),
            halstead_difficulty=Avg("halstead_difficulty"),
            halstead_difficulty_delta=Avg("halstead_difficulty_delta"),
            fan_in=Avg("fan_in"),
            fan_in_delta=Avg("fan_in_delta"),
            fan_out=Avg("fan_out"),
            fan_out_delta=Avg("fan_out_delta"),
            sloc=Sum("sloc"),
            sloc_delta=Sum("sloc_delta")
        )


class Package(models.Model):

    @classmethod
    def root(cls, branch):
        try:
            return Package.objects.get(parent=None, branch=branch)
        except Package.DoesNotExist:
            return None

    @classmethod
    def get(cls, name, branch):
        packages = name.split("/")
        parent = Package.root(branch)
        parent_name = ""

        for pkg in packages:
            pkg_name = "%s/%s" % (parent_name, pkg)

            package, created = Package.objects.get_or_create(
                name=pkg_name,
                branch=branch,
                parent=parent
            )

            parent = package
            parent_name = pkg_name

        return parent

    name = models.TextField()

    branch = models.ForeignKey("Branch", null=True)
    parent = models.ForeignKey("Package", null=True, related_name="children")

    left = models.IntegerField(default=0)
    right = models.IntegerField(default=0)

    def __unicode__(self):
        return self.name

    def add_package(self, package):
        package.parent = self

        package.save()

    def update(self, position=0):
        self.left = position

        for child in self.children.all():
            position = child.update(position + 1)

        self.right = position + 1

        self.save()

        return self.right

    def json(self):
        return {
            "href": utils.href(Package, self.id),
            "rel": "package",
            "rep": {
                "name": self.name,
                "branch": utils.href(Branch, self.branch_id),
                "parent": utils.href(Package, self.parent_id) if self.parent_id else None
            }
        }

    def parse_result(self, cursor):
        cols = [info[0] for info in cursor.description]

        result = {}
        values = cursor.fetchone()

        for index, col in enumerate(cols):
            result[col] = values[index]

        return result

    def all_children(self):
        return Package.objects.filter(left__gt=self.left, right__lt=self.right)

    def is_leaf(self):
        return self.right == self.left + 1


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

    revision = models.ForeignKey("Revision", related_name="files")
    author = models.ForeignKey("Author", related_name="files", null=True)
    date = models.DateTimeField(null=True)

    name = models.CharField(max_length=255)
    package = models.TextField()
    pkg = models.ForeignKey("Package", related_name="files", null=True)

    faulty = models.BooleanField(default=False)

    mimetype = models.CharField(max_length=255, null=True)

    change_type = models.CharField(max_length=1, null=True, choices=CHANGE_TYPES)
    copy_of = models.ForeignKey("File", null=True)

    cyclomatic_complexity = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    cyclomatic_complexity_delta = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    halstead_volume = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    halstead_volume_delta = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    halstead_difficulty = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    halstead_difficulty_delta = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    fan_in = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    fan_in_delta = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    fan_out = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    fan_out_delta = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    sloc = models.IntegerField(default=0)
    sloc_delta = models.IntegerField(default=0)

    sloc_squale = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    sloc_squale_delta = models.DecimalField(max_digits=15, decimal_places=2, default=0)

    lines_added = models.IntegerField(default=0)
    lines_removed = models.IntegerField(default=0)

    def __unicode__(self):
        return "name:\t\t%s\npackage:\t%s\nmimetype:\t%s\nchange type:\t%s" % (
            self.name,
            self.package,
            self.mimetype,
            self.change_type
        )

    def json(self, previous=None):
        if previous:
            complexity = previous["complexity"]
            structure = previous["structure"]

            cyclomatic_complexity = complexity["cyclomatic_complexity"] + float(self.cyclomatic_complexity_delta)
            halstead_difficulty = complexity["halstead_difficulty"] + float(self.halstead_difficulty_delta)
            halstead_volume = complexity["halstead_volume"] + float(self.halstead_volume_delta)

            fan_in = structure["fan_in"] + float(self.fan_in_delta)
            fan_out = structure["fan_out"] + float(self.fan_out_delta)
            sloc = structure["sloc_absolute"] + self.sloc_delta
            sloc_squale = structure["sloc"] + float(self.sloc_squale_delta)
        else:
            cyclomatic_complexity = float(self.cyclomatic_complexity)
            halstead_difficulty = float(self.halstead_difficulty)
            halstead_volume = float(self.halstead_volume)

            fan_in = float(self.fan_in)
            fan_out = float(self.fan_out)
            sloc = self.sloc
            sloc_squale = float(self.sloc_squale)

        return {
            "href": utils.href(File, self.id),
            "view": utils.view(File, self.id),
            "rel": "file",
            "rep": {
                "revision": utils.href(Revision, self.revision_id),
                "author": utils.href(Author, self.author_id),
                "date": self.date.isoformat(),
                "name": self.name,
                "package": self.package,
                "mimetype": self.mimetype,
                "changeType": self.change_type,
                "copyOf": utils.href(File, self.copy_of_id) if self.copy_of else None,
                "complexity": {
                    "cyclomatic_complexity": cyclomatic_complexity,
                    "cyclomatic_complexity_delta": float(self.cyclomatic_complexity_delta),
                    "halstead_volume": halstead_volume,
                    "halstead_volume_delta": float(self.halstead_volume_delta),
                    "halstead_difficulty": halstead_difficulty,
                    "halstead_difficulty_delta": float(self.halstead_difficulty_delta)
                },
                "structure": {
                    "fan_in": fan_in,
                    "fan_in_delta": float(self.fan_in_delta),
                    "fan_out": fan_out,
                    "fan_out_delta": float(self.fan_out_delta),
                    "sloc_absolute": sloc,
                    "sloc_absolute_delta": self.sloc_delta,
                    "sloc": sloc_squale,
                    "sloc_delta": float(self.sloc_squale_delta)
                },
                "churn": {
                    "added": self.lines_added,
                    "removed": self.lines_removed,
                    "churned_to_total": self.lines_added / sloc if sloc else 0,
                    "deleted_to_total": self.lines_removed / sloc if sloc else 0,
                    "churned_to_deleted": self.lines_added / self.lines_removed if self.lines_removed else 0
                }

            }
        }

    def get_previous(self, faulty=False):
        if self.change_type == Action.ADD:
            return None

        return utils.previous(File, self, {
            "name": self.name,
            "faulty": faulty,
            "pkg": self.pkg
        })

    def add_measures(self, measures):
        self.cyclomatic_complexity = measures["cyclomatic_complexity"]

        self.halstead_volume = measures["halstead_volume"]
        self.halstead_difficulty = measures["halstead_difficulty"]

        self.fan_in = measures["fan_in"]
        self.fan_out = measures["fan_out"]
        self.sloc = measures["sloc_absolute"]
        self.sloc_squale = measures["sloc"]

        previous = self.get_previous()

        if previous:
            self.cyclomatic_complexity_delta = self.cyclomatic_complexity - previous.cyclomatic_complexity

            self.halstead_volume_delta = self.halstead_volume - previous.halstead_volume
            self.halstead_difficulty_delta = self.halstead_difficulty - previous.halstead_difficulty

            self.fan_in_delta = self.fan_in - previous.fan_in
            self.fan_out_delta = self.fan_out - previous.fan_out
            self.sloc_delta = self.sloc - previous.sloc
            self.sloc_squale_delta = self.sloc_squale - previous.sloc_squale


        # If all priort revisions are faulty we pretend that this was the initial version
        # in order to minimize peaks in the delta curve for the metrics.
        if not previous and self.change_type == Action.MODIFY:
            self.change_type = Action.ADD

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

    @classmethod
    def add_fake_name(cls, author, names):
        index = author.id % len(names)

        author.fake_name = names[index]

        author.save()

    @classmethod
    def get(cls, href):
        pk = href.replace("/author/", "")

        return cls.objects.get(pk=pk)


    name = models.CharField(max_length=255)
    fake_name = models.CharField(max_length=255, null=True)

    email = models.EmailField(null=True)

    def __unicode__(self):
        if self.get_email():
            return "%s (%s)" % (self.get_name(), self.get_email())

        return self.get_name()

    def revision_count(self, branch=None, active=False):
        return self.get_revisions(branch=branch, active=active).count()

    def get_icon(self):
        size = 40
        mail = ""

        if self.get_email():
            mail = md5(self.get_email().lower()).hexdigest()

        params = urlencode({
            's': str(size)
        })

        return "http://www.gravatar.com/avatar/%s?%s" % (mail, params)

    def get_prime_language(self, branch=None):
        files = self.get_files(branch=branch, languages=File.KNOWN_LANGUAGES)\
                            .values("mimetype")\
                            .annotate(count=Count("mimetype"))\
                            .order_by("-count")

        if not files:
            return None

        return files[0]

    def get_complexity_index(self, branch=None):
        aggregate = self.get_files(branch=branch).aggregate(
            cyclomatic=Sum("cyclomatic_complexity_delta"),
            halstead_difficulty=Sum("halstead_difficulty_delta"),
            halstead_volume=Sum("halstead_volume_delta")
        )

        cyclomatic = aggregate["cyclomatic"] or 0
        halstead_volume = aggregate["halstead_volume"] or 0
        halstead_difficulty = aggregate["halstead_difficulty"] or 0

        return {
            "cyclomatic": float(cyclomatic),
            "halstead": {
                "volume": float(halstead_volume),
                "difficulty": float(halstead_difficulty)
            },
            "combined": float(
                cyclomatic +
                halstead_volume +
                halstead_difficulty
            )
        }

    def get_age(self, branch=None):
        timeframe = self.get_revisions(branch=branch).aggregate(start=Min("date"), end=Max("date"))

        return timeframe["start"], timeframe["end"]

    def get_work_index(self, branch=None):
        revisions = self.get_revisions(branch)

        all_revisions = revisions.count()
        revisions_per_day = revisions.values("day", "year", "month").distinct().count()

        return Fraction(all_revisions, revisions_per_day)

    def classify(self, branch=None):
        files = self.get_files(branch=branch).count()
        frontend = self.get_files(branch=branch, languages=Classify.frontend()).count()
        backend = self.get_files(branch=branch, languages=Classify.backend()).count()

        return {
            "frontend": float(Fraction(frontend, files)) if files else 0,
            "backend": float(Fraction(backend, files)) if files else 0
        }

    def get_revisions(self, branch=None, active=False):
        filters = {
            "author": self
        }

        if branch:
            filters["branch"] = branch

        if branch and active:
            filters["date__gte"] = branch.analyzed_date - timedelta(days=IMPACT_TIME_PERIOD)

        return Revision.objects.filter(**filters).distinct()

    def get_files(self, branch=None, languages=None, mine=True):
        filters = {}

        if mine:
            filters["author"] = self

        if branch:
            filters["revision__branch"] = branch

        if languages:
            filters["mimetype__in"] = languages

        return File.objects.filter(**filters).distinct()

    def get_name(self):
        if ANONYMIZE:
            return self.fake_name

        return self.name

    def get_email(self):
        if ANONYMIZE:
            first, last = self.fake_name.split(" ")

            return "%s.%s@example.com" % (first.lower(), last.lower())

        return self.email


    def json(self, branch=None):
        start, end = self.get_age(branch)

        return {
            "href": utils.href(Author, self.id),
            "view": utils.view(Author, self.id),
            "rel": "author",
            "rep": {
                "id": self.id,
                "name": str(self),
                "age": str(end - start) if start and end else None,
                "firstAction": start.isoformat() if start else None,
                "lastAction": end.isoformat() if end else None,
                "workIndex": float(self.get_work_index(branch)),
                "icon": self.get_icon(),
                "revisions": {
                    "all": self.revision_count(branch),
                    "currentPeriod": self.revision_count(branch, active=True)
                },
                "primeLanguage": self.get_prime_language(branch)
            }
        }


@receiver(post_save, sender=Author)
def add_fake_name(sender, **kwargs):
    instance = kwargs["instance"]

    if instance.fake_name:
        return

    names = utils.get_names()

    Author.add_fake_name(instance, names)
