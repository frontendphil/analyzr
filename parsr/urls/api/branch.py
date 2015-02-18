from django.conf.urls import patterns, url, include

urlpatterns = patterns('parsr.api.branch',

    url(r"^$", "list"),

    url(r"^/(?P<branch_id>\d+)$", "info"),
    url(r'^/(?P<branch_id>\d+)/contributors$', 'contributors'),
)
