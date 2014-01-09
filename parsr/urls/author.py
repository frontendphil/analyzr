from django.conf.urls import patterns, url

urlpatterns = patterns('parsr.views.author',

    url(r"^$", "info"),
    url(r"^/view$", "view"),

    url(r'^/metrics$', 'metrics'),
    url(r'^/churn$', 'churn'),
    url(r'^/punchcard$', "punchcard"),
    url(r"^/packages$", "packages"),
    url(r"^/score$", "score"),
    url(r'^/stats$', "file_stats"),
    url(r'^/commits$', "commits"),

)
