from django.conf.urls import patterns, url, include
from django.contrib import admin

from parsr import models

admin.site.register(models.Repo)
admin.site.register(models.Revision)
admin.site.register(models.Author)
admin.site.register(models.File)
admin.site.register(models.Branch)

urlpatterns = patterns('',
    # url(r"^$", "parsr.views.app.index"),
    # url(r'^login$', "parsr.views.app.login"),
    # url(r'^logout$', "parsr.views.app.logout"),

    url(r"^api/repositories$", "parsr.views.repo.list"),
    url(r"^api/repository/(?P<repository_id>\d+)", include("parsr.urls.repo")),

    # url(r"^repo/create$", "parsr.views.repo.create"),
    # url(r"^repo/create/save$", "parsr.views.repo.save"),
    # url(r"^repo/(?P<repo_id>\d+)", include("parsr.urls.repo")),

    # url(r"^api/branches", "parsr.views.branch.list"),
    # url(r"^api/branch/(?P<branch_id>\d+)", include("parsr.urls.branch")),
    # url(r"^author/(?P<author_id>\d+)", include("parsr.urls.author")),
    # url(r"^revision/(?P<revision_id>\d+)", include("parsr.urls.revision")),
    # url(r"^file/(?P<file_id>\d+)", include("parsr.urls.file")),
    # url(r"^package/(?P<package_id>\d+)", include("parsr.urls.package")),

    url(r"^.*", "parsr.views.app.index"),
)
