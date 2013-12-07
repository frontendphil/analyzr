from django.conf.urls import patterns, url

urlpatterns = patterns('parsr.views.revision',

    url(r"^$", "info"),
    url(r"^/view$", "view"),

)
