import json
import traceback
import sys

from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.http import require_POST
from django.template import RequestContext
from django.http import HttpResponse

from parsr.models import Repo, Author, Branch
from parsr.forms import RepoForm


def index(request):
    repositories = Repo.objects.all()

    return render_to_response("index.html", { "repositories": repositories }, context_instance=RequestContext(request))


def create(request):
    form = RepoForm()

    return render_to_response("create.html",
        {
            "form": form
        }, context_instance=RequestContext(request))


@require_POST
def save(request):
    form = RepoForm(request.POST)

    if not form.is_valid():
        return HttpResponse(json.dumps(form.errors), status=403, mimetype="application/json")

    try:
        form.save()
    except:
        return HttpResponse(json.dumps({"repo": True}), status=500, mimetype="application/json")

    return HttpResponse(status=200)


@require_POST
def remove(request, repo_id):
    repo = get_object_or_404(Repo, pk=repo_id)

    repo.delete()

    return HttpResponse(status=200)


def edit(request, repo_id):
    repo = get_object_or_404(Repo, pk=repo_id)
    form = RepoForm(instance=repo)

    return render_to_response("edit.html",
        {
            "form": form
        }, context_instance=RequestContext(request))


def repo(request, id):
    repo = get_object_or_404(Repo, pk=id)

    return render_to_response("repo.html",
        {
            "repo": repo
        }, context_instance=RequestContext(request))


def author(request, id):
    author = get_object_or_404(Author, pk=id)

    return render_to_response("author.html",
        {
            "author": author
        }, context_instance=RequestContext(request))


def punchcard(request, repo_id, author_id=None):
    repo = get_object_or_404(Repo, pk=repo_id)
    author = get_object_or_404(Author, pk=author_id) if author_id else None

    return HttpResponse(json.dumps(repo.punchcard(author)), mimetype="application/json")


def file_stats(request, repo_id, author_id=None):
    repo = get_object_or_404(Repo, pk=repo_id)
    author = get_object_or_404(Author, pk=author_id) if author_id else None

    return HttpResponse(json.dumps(repo.file_statistics(author)), mimetype="application/json")


def commits(request, repo_id, author_id=None):
    repo = get_object_or_404(Repo, pk=repo_id)
    author = get_object_or_404(Author, pk=author_id) if author_id else None

    return HttpResponse(json.dumps(repo.commit_history(author)), mimetype="application/json")


@require_POST
def analyze(request, repo_id, branch_id):
    repo = get_object_or_404(Repo, pk=repo_id)
    branch = get_object_or_404(Branch, pk=branch_id)

    try:
        repo.analyze(branch)
    except Exception:
        traceback.print_exc(file=sys.stdout)

        repo.abort_analyze()

    return HttpResponse(json.dumps({ "status": "ok" }), mimetype="application/json")
