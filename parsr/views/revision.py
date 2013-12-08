from django.shortcuts import get_object_or_404

from annoying.decorators import render_to, ajax_request

from parsr.models import Revision


def get_revision(rev_id):
    return get_object_or_404(Revision, pk=rev_id)


@render_to("revision.html")
def view(request, rev_id):
    revision = get_revision(rev_id)

    return { revision: revision }


@ajax_request
def info(request, rev_id):
    revision = get_revision(rev_id)

    return revision.json()
