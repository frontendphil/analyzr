from django.conf.urls import patterns, url

urlpatterns = patterns('parsr.views.file',

    url(r"^$", "info"),
    url(r"^/view$", "view"),

)
