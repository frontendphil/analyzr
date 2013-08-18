import json

from django.shortcuts import render_to_response, get_object_or_404
from django.views.decorators.http import require_POST
from django.template import RequestContext
from django.http import HttpResponse

from parsr.models import Repo


def index(request):
    repositories = Repo.objects.all()

    return render_to_response("index.html", { "repositories": repositories }, context_instance=RequestContext(request))


def repo(request, id):
    repo = get_object_or_404(Repo, pk=id)

    return render_to_response("repo.html",
        {
            "repo": repo
        }, context_instance=RequestContext(request))


@require_POST
def analyze(request, id):
    repo = get_object_or_404(Repo, pk=id)
    repo.analyze()

    return HttpResponse(json.dumps({ "status": "ok" }), mimetype="application/json")
