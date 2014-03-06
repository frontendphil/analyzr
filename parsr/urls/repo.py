from django.conf.urls import patterns, url

urlpatterns = patterns('parsr.views.repo',

    url(r"^$", "info"),

    url(r"^/branch/(?P<branch_id>\d+)", "view", name="repository-view"),

    url(r"^/branches$", "branches"),
    url(r"^/view$", "view"),
    url(r"^/edit$", "edit"),
    url(r"^/remove$", "remove"),
    url(r"^/purge$", "purge"),
    url(r"^/update$", "update"),

)
