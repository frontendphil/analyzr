import traceback

from pygments import highlight
from pygments.lexers import PythonTracebackLexer
from pygments.formatters import HtmlFormatter

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.core.urlresolvers import reverse

from annoying.decorators import ajax_request

from parsr.models import Branch
from parsr.utils import send_mail
from parsr.views.author import parse_filters


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


def view(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    return HttpResponseRedirect(reverse("parsr.views.repo.view", kwargs={
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
    branch = get_branch(branch_id)

    return branch.json()


@ajax_request
def commits(request, branch_id):
    branch = get_branch(branch_id)

    return branch.commit_history()


@ajax_request
def punchcard(request, branch_id):
    branch = get_branch(branch_id)

    return branch.punchcard()


@ajax_request
def file_stats(request, branch_id):
    branch= get_branch(branch_id)

    return branch.file_statistics()


@ajax_request
def contributors(request, branch_id):
    branch = get_branch(branch_id)

    page = request.GET.get("page")

    return branch.contributors(page=page)


@ajax_request
def packages(request, branch_id):
    branch = get_branch(branch_id)

    return branch.packages()


@ajax_request
def metrics(request, branch_id):
    branch = get_branch(branch_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.metrics(language=language, package=package, start=start, end=end)


@ajax_request
def churn(request, branch_id):
    branch = get_branch(branch_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.churn(language=language, package=package, start=start, end=end)


@ajax_request
def score(request, branch_id):
    branch = get_branch(branch_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.score(language=language)


@ajax_request
def impact(request, branch_id):
    branch = get_branch(branch_id)

    return branch.impact()


@ajax_request
def cleanup(request, branch_id):
    branch = get_branch(branch_id)

    branch.cleanup()

    return {"status": "ok"}
