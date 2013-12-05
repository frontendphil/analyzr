from django.shortcuts import get_object_or_404

from annoying.decorators import ajax_request, render_to

from parsr.models import Author


@render_to("author.html")
def index(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    return { "author": author }


@ajax_request
def info(request, author_id):
    author = get_object_or_404(Author, pk=author_id)

    return author.json()
