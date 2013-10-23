import json
import traceback
import sys

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from annoying.decorators import render_to, ajax_request
from annoying.functions import get_object_or_None

from parsr.models import Repo, Author, Branch
from parsr.forms import RepoForm


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


@render_to("repo.html")
def repo(request, repo_id, branch_id=None):
    repo = get_object_or_404(Repo, pk=repo_id)
    branch = get_object_or_404(Branch, pk=branch_id) if branch_id else repo.default_branch()

    return { "repo": repo, "branch": branch }


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
@require_POST
def analyze(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    try:
        branch.analyze()
    except Exception:
        traceback.print_exc(file=sys.stdout)

        branch.abort_analyze()

    return { "status": "ok" }


@ajax_request
@require_POST
def measure(request, branch_id):
    branch = get_object_or_404(Branch, pk=branch_id)

    try:
        branch.measure()
    except Exception:
        traceback.print_exc(file=sys.stdout)

        branch.abort_measure()

    return { "status": "ok" }
