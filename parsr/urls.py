from django.conf.urls import patterns, url
from django.contrib import admin

from parsr.models import Repo, Revision, Author, File

admin.site.register(Repo)
admin.site.register(Revision)
admin.site.register(Author)
admin.site.register(File)

urlpatterns = patterns('parsr.views',
    url(r"^$", "index"),
    url(r"^repo/(?P<repo_id>\d+)/$", "repo"),
    url(r"^repo/(?P<repo_id>\d+)/branch/(?P<branch_id>\d+)/$", "repo"),
    url(r'^author/(?P<author_id>\d+)/branch/(?P<branch_id>\d+)/$', 'author'),

    url(r'^commits/branch/(?P<branch_id>\d+)/author/(?P<author_id>\d+)/$', "commits"),
    url(r'^commits/branch/(?P<branch_id>\d+)/$', "commits"),

    url(r'^file_stats/branch/(?P<branch_id>\d+)/author/(?P<author_id>\d+)/$', "file_stats"),
    url(r'^file_stats/branch/(?P<branch_id>\d+)/$', "file_stats"),

    url(r'^contributors/branch/(?P<branch_id>\d+)$', 'contributors'),

    url(r'^metrics/branch/(?P<branch_id>\d+)/author/(?P<author_id>\d)/$', 'metrics'),

    url(r'^punchcard/branch/(?P<branch_id>\d+)/author/(?P<author_id>\d+)/$', "punchcard"),
    url(r'^punchcard/branch/(?P<branch_id>\d+)$', "punchcard"),

    url(r"^analyze/branch/(?P<branch_id>\d+)/$", "analyze"),
    url(r"^measure/branch/(?P<branch_id>\d+)/$", "measure"),

    url(r"^create/$", "create"),
    url(r"^create/save/$", "save"),

    url(r"^edit/(?P<repo_id>\d+)/$", "edit"),

    url(r"^remove/(?P<repo_id>\d+)/$", "remove"),
)
