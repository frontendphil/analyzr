from django.conf.urls import patterns, url

urlpatterns = patterns('parsr.api.branch',

    url(r"^$", "list"),

    url(r"^/(?P<branch_id>\d+)$", "info"),
    url(r'^/(?P<branch_id>\d+)/contributors$', 'contributors'),
    url(r'^/(?P<branch_id>\d+)/activity$', "punchcard"),
    url(r'^/(?P<branch_id>\d+)/churn$', 'churn'),
)
