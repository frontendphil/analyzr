from django.shortcuts import get_object_or_404

from annoying.decorators import ajax_request

from parsr.models import Repo


# @login_required
@ajax_request
def info(request, repository_id):
    repo = get_object_or_404(Repo, pk=repository_id)

    return repo.json()


# @login_required
@ajax_request
def list(request):
    repos = Repo.objects.all().order_by("-url")

    return [repo.json() for repo in repos]
