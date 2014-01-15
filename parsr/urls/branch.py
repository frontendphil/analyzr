from django.conf.urls import patterns, url, include

urlpatterns = patterns('parsr.views.branch',

    url(r"^$", "info"),

    url(r"^/view$", "view"),
    url(r'^/contributors$', 'contributors'),
    url(r'^/commits$', "commits"),
    url(r'^/stats$', "file_stats"),
    url(r'^/punchcard$', "punchcard"),

    url(r"^/analyze$", "analyze"),
    url(r"^/analyze/resume$", "resume_analyze"),

    url(r"^/measure$", "measure"),
    url(r"^/measure/resume$", "resume_measure"),

    url(r"^/packages$", "packages"),
    url(r"^/metrics$", "metrics"),

    url(r"^/author/(?P<author_id>\d+)", include("parsr.urls.author")),
)
