from django.conf.urls import patterns, url

urlpatterns = patterns('parsr.views.package',

    url(r"^$", "info"),
    url(r"^/view$", "view"),

)
