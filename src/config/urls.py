"""URL configuration for statspubliques project."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from stats.views import Main

urlpatterns = [
    path(f"{settings.ADMIN_SLUG}/", admin.site.urls),
    path("", Main.as_view(), name="main"),
    path("stats/", include("stats.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("__debug__/", include("debug_toolbar.urls")),
    ]
