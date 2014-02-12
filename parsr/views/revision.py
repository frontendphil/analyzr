from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from annoying.decorators import render_to, ajax_request

from parsr.models import Revision


def get_revision(revision_id):
    return get_object_or_404(Revision, pk=revision_id)


@login_required
@render_to("revision.html")
def view(request, revision_id):
    revision = get_revision(revision_id)

    return { revision: revision }


@login_required
@ajax_request
def info(request, revision_id):
    revision = get_revision(revision_id)

    return revision.json()
