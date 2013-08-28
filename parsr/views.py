import json

from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.http import require_POST
from django.template import RequestContext
from django.http import HttpResponse

from parsr.models import Repo, Author


def index(request):
    repositories = Repo.objects.all()

    return render_to_response("index.html", { "repositories": repositories }, context_instance=RequestContext(request))


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



@require_POST
def analyze(request, id):
    repo = get_object_or_404(Repo, pk=id)

    try:
        repo.analyze()
    except:
        repo.abort_analyze()

    return HttpResponse(json.dumps({ "status": "ok" }), mimetype="application/json")
