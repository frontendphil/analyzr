from datetime import datetime

from dateutil import parser

from django.shortcuts import get_object_or_404

from annoying.decorators import ajax_request, render_to
from annoying.functions import get_object_or_None

from parsr.views.branch import get_branch_and_author
from parsr.models import Author, Package


def parse_filters(request, branch):
    language = request.GET.get("language")
    package = get_object_or_None(Package, pk=request.GET.get("package"))

    start, end = parse_date_range(request, branch)

    return language, package, start, end


def parse_date_range(request, branch):
    start = request.GET.get("from")
    end = request.GET.get("to")

    tzinfo = get_tzinfo(branch.repo.timezone)

    start = parser.parse(start, tzinfos=tzinfo) if start else None
    end = parser.parse(end, tzinfos=tzinfo) if end else None

    return start, end


def get_tzinfo(timezone):
    now = datetime.now()
    tz_abbr = timezone.tzname(now)

    tzinfo = {}
    tzinfo[tz_abbr] = timezone.zone

    return tzinfo


@render_to("author.html")
def view(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    return { "branch": branch, "author": author }


@ajax_request
def info(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    return author.json()


@ajax_request
def metrics(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.metrics(author, language=language, package=package, start=start, end=end)


@ajax_request
def commits(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    return branch.commit_history(author)


@ajax_request
def file_stats(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    return branch.file_statistics(author)


@ajax_request
def punchcard(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    return branch.punchcard(author)


@ajax_request
def churn(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.churn(author, language=language, package=package, start=start, end=end)


@ajax_request
def packages(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    return branch.packages(author)


@ajax_request
def score(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    return branch.score(author)
