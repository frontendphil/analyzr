import traceback

from dateutil import parser

from datetime import datetime

from pygments import highlight
from pygments.lexers import PythonTracebackLexer
from pygments.formatters import HtmlFormatter

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse

from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None

from parsr.models import Branch, Author
from parsr.utils import send_mail


def get_branch_and_author(branch_id, author_id):
    branch = get_object_or_404(Branch, pk=branch_id)
    author = get_object_or_None(Author, pk=author_id)

    return branch, author


def track_action(branch, action, abort):
    try:
        action()
    except:
        tb = "".join(traceback.format_exc())

        lexer = PythonTracebackLexer()
        formatter = HtmlFormatter(noclasses=True)

        error = highlight(tb, lexer, formatter)

        abort(error)
        send_mail(tb)

    return { "status": "ok" }


def get_branch(branch_id):
    return get_object_or_404(Branch, pk=branch_id)


def get_tzinfo(timezone):
    now = datetime.now()
    tz_abbr = timezone.tzname(now)

    tzinfo = {}
    tzinfo[tz_abbr] = timezone.zone

    return tzinfo


def parse_filters(request, branch):
    language = request.GET.get("language")

    start, end = parse_date_range(request, branch)

    return language, start, end


def parse_date_range(request, branch):
    start = request.GET.get("from")
    end = request.GET.get("to")

    tzinfo = get_tzinfo(branch.repo.timezone)

    start = parser.parse(start, tzinfos=tzinfo) if start else None
    end = parser.parse(end, tzinfos=tzinfo) if end else None

    return start, end


def view(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    return HttpResponseRedirect(reverse("parsr.views.repo", kwargs={
        "branch_id": branch.id,
        "repo_id": branch.repo.id
    }))


@ajax_request
@require_POST
def analyze(request, branch_id):
    branch = get_branch(branch_id)

    return track_action(branch, lambda: branch.analyze(), lambda x: branch.abort_analyze(x))


@ajax_request
@require_POST
def resume_analyze(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    return track_action(branch, lambda: branch.analyze(resume=True), lambda x: branch.abort_analyze(x))


@ajax_request
@require_POST
def measure(request, branch_id):
    branch = get_branch(branch_id)

    return track_action(branch, lambda: branch.measure(), lambda x: branch.abort_measure(x))


@ajax_request
@require_POST
def resume_measure(request, branch_id):
    branch = get_branch(branch_id)

    return track_action(branch, lambda: branch.measure(resume=True), lambda x: branch.abort_measure(x))


@ajax_request
def info(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    return branch.json()


@render_to("author.html")
def author(request, author_id, branch_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    return { "author": author, "branch": branch }


@ajax_request
def punchcard(request, branch_id, author_id=None):
    branch, author = get_branch_and_author(branch_id, author_id)

    return branch.punchcard(author)


@ajax_request
def file_stats(request, branch_id, author_id=None):
    branch, author = get_branch_and_author(branch_id, author_id)

    return branch.file_statistics(author)


@ajax_request
def commits(request, branch_id, author_id=None):
    branch, author = get_branch_and_author(branch_id, author_id)

    return branch.commit_history(author)


@ajax_request
def metrics(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    language, start, end = parse_filters(request, branch)

    return branch.metrics(author, language=language, start=start, end=end)


@ajax_request
def churn(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    language, start, end = parse_filters(request, branch)

    return branch.churn(author, language=language, start=start, end=end)


@ajax_request
def contributors(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    page = request.GET.get("page")

    return branch.contributors(page=page)
