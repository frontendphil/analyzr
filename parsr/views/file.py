from django.shortcuts import get_object_or_404

from annoying.decorators import render_to, ajax_request

from parsr.models import File


def get_file(file_id):
    return get_object_or_404(File, pk=file_id)


@render_to("file.html")
def view(request, file_id):
    f = get_file(file_id)

    return { "file": f }


@ajax_request
def info(request, file_id):
    f = get_file(file_id)

    return f.json()
