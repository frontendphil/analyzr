from django.conf.urls import patterns, url

urlpatterns = patterns('parsr.views.author',

    url(r"^$", "index"),
    url(r"^/info$", "info"),

)
