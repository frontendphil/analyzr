from django.shortcuts import get_object_or_404

from annoying.decorators import render_to, ajax_request

from parsr.models import Author


@render_to("index.html")
def index(request):
    return {}


@ajax_request
def author(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    return author.json()
