from django.conf.urls import patterns, url, include
from django.contrib import admin

from parsr import models

admin.site.register(models.Repo)
admin.site.register(models.Revision)
admin.site.register(models.Author)
admin.site.register(models.File)
admin.site.register(models.Branch)

urlpatterns = patterns('',
    url(r"^$", "parsr.views.app.index"),

    url(r"^repositories$", "parsr.views.repo.list"),

    url(r"^repo/create$", "parsr.views.repo.create"),
    url(r"^repo/create/save$", "parsr.views.repo.save"),
    url(r"^repo/(?P<repo_id>\d+)", include("parsr.urls.repo")),

    url(r"^branch/(?P<branch_id>\d+)", include("parsr.urls.branch")),
    url(r"^author/(?P<author_id>\d+)", include("parsr.urls.author")),
)
