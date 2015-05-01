import traceback

from pygments import highlight
from pygments.lexers import PythonTracebackLexer
from pygments.formatters import HtmlFormatter

from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.views.decorators.gzip import gzip_page
from django.contrib.auth.decorators import login_required

from annoying.decorators import ajax_request, render_to

from parsr.models import Branch
from parsr.utils import send_error
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
        send_error(tb)

    return { "status": "ok" }


def get_branch(branch_id):
    return get_object_or_404(Branch, pk=branch_id)


@login_required
def view(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    if not branch.analyzed:
        return redirect("parsr.views.app.index")

    return redirect("repository-view", branch_id=branch.id, repo_id=branch.repo.id)


@login_required
@ajax_request
@require_POST
def analyze(request, branch_id):
    branch = get_branch(branch_id)

    return track_action(branch, lambda: branch.analyze(), lambda x: branch.abort_analyze(x))


@login_required
@ajax_request
@require_POST
def resume_analyze(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    return track_action(branch, lambda: branch.analyze(resume=True), lambda x: branch.abort_analyze(x))


@login_required
@ajax_request
@require_POST
def measure(request, branch_id):
    branch = get_branch(branch_id)

    return track_action(branch, lambda: branch.measure(), lambda x: branch.abort_measure(x))


@login_required
@ajax_request
@require_POST
def resume_measure(request, branch_id):
    branch = get_branch(branch_id)

    return track_action(branch, lambda: branch.measure(resume=True), lambda x: branch.abort_measure(x))


@login_required
@ajax_request
def info(request, branch_id):
    branch = get_branch(branch_id)

    return branch.json()


@login_required
@ajax_request
def commits(request, branch_id):
    branch = get_branch(branch_id)

    return branch.commit_history()


@login_required
@ajax_request
def file_stats(request, branch_id):
    branch= get_branch(branch_id)

    return branch.file_statistics()


@ajax_request
def contributors(request, branch_id):
    branch = get_branch(branch_id)

    page = request.GET.get("page")

    return branch.contributors(page=page)


@login_required
@gzip_page
@ajax_request
def packages(request, branch_id):
    branch = get_branch(branch_id)

    return branch.packages()


@login_required
@gzip_page
@ajax_request
def metrics(request, branch_id):
    branch = get_branch(branch_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.metrics(language=language, package=package, start=start, end=end)


@login_required
@ajax_request
def score(request, branch_id):
    branch = get_branch(branch_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.score(language=language)


@login_required
@ajax_request
def impact(request, branch_id):
    branch = get_branch(branch_id)

    return branch.impact()


@login_required
@ajax_request
def cleanup(request, branch_id):
    branch = get_branch(branch_id)

    branch.cleanup()

    return {"status": "ok"}


@login_required
@gzip_page
@ajax_request
def experts(request, branch_id):
    branch = get_branch(branch_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.experts(language=language, package=package, start=start, end=end)


@login_required
@render_to("experts.html")
def experts_detail(request, branch_id):
    return { "branch": get_branch(branch_id) }


@login_required
@gzip_page
@ajax_request
def uberexperts(request, branch_id):
    branch = get_branch(branch_id)

    language, package, start, end = parse_filters(request, branch)

    return branch.get_current_top_authors(language, package=package, start=start, end=end)
