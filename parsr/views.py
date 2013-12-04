import json
import traceback
import sys

from dateutil import parser

from pygments import highlight
from pygments.lexers import PythonTracebackLexer
from pygments.formatters import HtmlFormatter

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponse, HttpResponseRedirect
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.urlresolvers import reverse

from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None

from parsr.models import Repo, Author, Branch
from parsr.forms import RepoForm
from parsr.utils import send_mail


def get_branch_and_author(branch_id, author_id):
    branch = get_object_or_404(Branch, pk=branch_id)
    author = get_object_or_None(Author, pk=author_id)

    return branch, author


@render_to("index.html")
def index(request):
    repositories = Repo.objects.all()

    return { "repositories": repositories }


@render_to("create.html")
def create(request):
    form = RepoForm()

    return { "form": form }


@require_POST
def save(request):
    form = RepoForm(request.POST)

    if not form.is_valid():
        return HttpResponse(json.dumps(form.errors), status=403, mimetype="application/json")

    instance = None

    try:
        instance = form.save()
    except Exception:
        traceback.print_exc(file=sys.stdout)

        if instance:
            instance.delete()

        return HttpResponse(json.dumps({"repo": True}), status=500, mimetype="application/json")

    return HttpResponse(status=200)


@require_POST
def remove(request, repo_id):
    repo = get_object_or_404(Repo, pk=repo_id)

    for branch in repo.branches():
        branch.cleanup()

    repo.delete()

    return HttpResponse(status=200)


@render_to("edit.html")
def edit(request, repo_id):
    repo = get_object_or_404(Repo, pk=repo_id)
    form = RepoForm(instance=repo)

    return { "form": form }


@ajax_request
def contributors(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    PER_PAGE = 10

    paginator = Paginator(branch.authors(), PER_PAGE)
    page = request.GET.get("page")

    try:
        authors = paginator.page(page)
    except PageNotAnInteger:
        page = 1
        authors = paginator.page(1)
    except EmptyPage:
        page = paginator.num_pages
        authors = paginator.page(paginator.num_pages)

    response = {
        "hasNext": not page == paginator.num_pages,
        "hasPrevious": not page == 1,
        "page": int(page),
        "pages": paginator.num_pages,
        "perPage": PER_PAGE,
        "authors": [author.json(branch) for author in authors]
    }

    return response


@ajax_request
def repos(request):
    repos = Repo.objects.all().order_by("-url")

    return [repo.json() for repo in repos]


@render_to("repo.html")
def repo(request, repo_id, branch_id=None):
    repo = get_object_or_404(Repo, pk=repo_id)
    branch = get_object_or_404(Branch, pk=branch_id) if branch_id else repo.default_branch()

    return { "repo": repo, "branch": branch }


def branch(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    return HttpResponseRedirect(reverse("parsr.views.repo", kwargs={
        "branch_id": branch.id,
        "repo_id": branch.repo.id
    }))


@ajax_request
def branch_info(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    return branch.json()


@ajax_request
def author(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    return author.json()


@render_to("author.html")
def branch_author(request, author_id, branch_id):
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

    language = request.GET.get("language")

    start = request.GET.get("from")
    end = request.GET.get("to")

    start = parser.parse(start, tzinfos=[branch.repo.timezone]) if start else None
    end = parser.parse(end, tzinfos=[branch.repo.timezone]) if end else None

    return branch.metrics(author, language=language, start=start, end=end)


@ajax_request
def churn(request, branch_id, author_id):
    branch, author = get_branch_and_author(branch_id, author_id)

    return branch.churn(author)


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
