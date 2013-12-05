from django.conf.urls import patterns, url

urlpatterns = patterns('parsr.views.repo',

    url(r"^$", "index"),
    url(r"^/branch/(?P<branch_id>\d+)", "index"),

    url(r"^/info$", "info"),
    url(r"^/edit$", "edit"),
    url(r"^/remove$", "remove"),

)
