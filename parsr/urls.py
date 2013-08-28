from django.conf.urls import patterns, url
from django.contrib import admin

from parsr.models import Repo, Revision, Author, File

admin.site.register(Repo)
admin.site.register(Revision)
admin.site.register(Author)
admin.site.register(File)

urlpatterns = patterns('parsr.views',
    url(r"^$", "index"),
    url(r"^repo/(?P<id>\d+)/$", "repo"),
    url(r'^author/(?P<id>\d+)/$', 'author'),
    url(r'^punchcard/repo/(?P<repo_id>\d+)/author/(?P<author_id>\d+)', "punchcard"),
    url(r'^punchcard/repo/(?P<repo_id>\d+)', "punchcard"),
    url(r"^analyze/(?P<id>\d+)/$", "analyze")
)
