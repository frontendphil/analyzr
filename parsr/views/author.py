from datetime import datetime

from dateutil import parser

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from annoying.decorators import ajax_request, render_to
from annoying.functions import get_object_or_None

from parsr.models import Author, Package, Branch


def get_branch_and_author(branch_id, author_id):
    branch = get_object_or_None(Branch, pk=branch_id)
    author = get_object_or_404(Author, pk=author_id)

    return branch, author


def get_branch(request):
    branch_id = request.GET.get("branch")

    if branch_id:
        return branch_id.replace("/branch/", "")

    return None


def parse_filters(request, branch):
    language = request.GET.get("language")

    pkg = request.GET.get("package")

    if pkg:
        pkg = pkg.replace("/package/", "")

    package = get_object_or_None(Package, pk=pkg)

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


@login_required
@render_to("author.html")
def view(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    if not branch.analyzed:
        return redirect("parsr.views.app.index")

    return { "branch": branch, "author": author }


@login_required
@ajax_request
def info(request, author_id):
    branch_id = get_branch(request)

    branch, author = get_branch_and_author(branch_id, author_id)

    return author.json(branch)


@login_required
@ajax_request
def metrics(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.metrics(author, language=language, package=package, start=start, end=end)


@login_required
@ajax_request
def commits(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    return branch.commit_history(author)


@login_required
@ajax_request
def file_stats(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    return branch.file_statistics(author=author)


@login_required
@ajax_request
def punchcard(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    return branch.punchcard(author)


@login_required
@ajax_request
def churn(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.churn(author, language=language, package=package, start=start, end=end)


@login_required
@ajax_request
def score(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.score(author=author, language=language)


@login_required
@render_to("compare.html")
def compare(request, branch_id, author_id, compare_id):
    branch, author = get_branch_and_author(branch_id, author_id)
    compare_to = get_object_or_404(Author, pk=compare_id)

    return { "branch": branch, "left": author, "right": compare_to }
