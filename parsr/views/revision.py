from django.shortcuts import get_object_or_404

from annoying.decorators import render_to, ajax_request

from parsr.models import Revision


def get_revision(identifier):
    return get_object_or_404(Revision, identifier=identifier)


@render_to("revision.html")
def view(request, identifier):
    revision = get_revision(identifier)

    return { revision: revision }


@ajax_request
def info(request, identifier):
    revision = get_revision(identifier)

    return revision.json()
