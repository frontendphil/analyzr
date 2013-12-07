import json
import traceback
import sys

from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from django.http import HttpResponse

from annoying.decorators import render_to, ajax_request

from parsr.models import Repo, Branch
from parsr.forms import RepoForm


@render_to("repo.html")
def view(request, repo_id, branch_id=None):
    repo = get_object_or_404(Repo, pk=repo_id)
    branch = get_object_or_404(Branch, pk=branch_id) if branch_id else repo.default_branch()

    return { "repo": repo, "branch": branch }


@ajax_request
def info(request, repo_id):
    repo = get_object_or_404(Repo, pk=repo_id)

    return repo.json()


@ajax_request
def list(request):
    repos = Repo.objects.all().order_by("-url")

    return [repo.json() for repo in repos]


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
