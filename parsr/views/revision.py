from django.shortcuts import get_object_or_404

from annoying.decorators import render_to, ajax_request

from parsr.models import Revision


def get_revision(revision_id):
    return get_object_or_404(Revision, pk=revision_id)


@render_to("revision.html")
def view(request, revision_id):
    revision = get_revision(revision_id)

    return { revision: revision }


@ajax_request
def info(request, revision_id):
    revision = get_revision(revision_id)

    return revision.json()
