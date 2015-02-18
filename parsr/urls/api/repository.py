from django.conf.urls import patterns, url, include

urlpatterns = patterns('parsr.api.repository',
    url(r"^$", "list"),
    url(r"^/(?P<repository_id>\d+)$", "info"),
    url(r"^/(?P<repository_id>\d+)/branches", include("parsr.urls.api.branch")),
)
