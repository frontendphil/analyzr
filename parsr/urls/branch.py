from django.conf.urls import patterns, url

urlpatterns = patterns('parsr.views.branch',

    url(r"^$", "index"),

    url(r"^/info$", "info"),
    url(r'^/contributors$', 'contributors'),

    url(r'^/author/(?P<author_id>\d+)$', 'author'),

    url(r'^/author/(?P<author_id>\d+)/commits$', "commits"),
    url(r'^/commits$', "commits"),

    url(r'^/author/(?P<author_id>\d+)/stats$', "file_stats"),
    url(r'^/stats$', "file_stats"),

    url(r'^/author/(?P<author_id>\d+)/metrics$', 'metrics'),
    url(r'^/author/(?P<author_id>\d+)/churn$', 'churn'),
    url(r'^/author/(?P<author_id>\d+)/punchcard$', "punchcard"),
    url(r'^/punchcard$', "punchcard"),

    url(r"^/analyze$", "analyze"),
    url(r"^/analyze/resume$", "resume_analyze"),

    url(r"^/measure$", "measure"),
    url(r"^/measure/resume$", "resume_measure"),

)
