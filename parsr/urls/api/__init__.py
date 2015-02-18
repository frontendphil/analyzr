from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r"^/repositories", include("parsr.urls.api.repository")),
)
