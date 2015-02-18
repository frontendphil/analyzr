from django.conf.urls import patterns, url, include

urlpatterns = patterns('',
    url(r"^api/repositories", include("parsr.urls.api.repository")),
    url(r"^api/repositories/(?P<repository_id>\d+)", include("parsr.urls.repo")),
)
