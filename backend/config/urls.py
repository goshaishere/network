from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.common.urls")),
    path("api/v1/", include("apps.accounts.urls")),
    path("api/v1/", include("apps.profiles.urls")),
    path("api/v1/", include("apps.walls.urls")),
    path("api/v1/", include("apps.communities.urls")),
    path("api/v1/", include("apps.messaging.urls")),
    path("api/v1/", include("apps.media.urls")),
    path("api/v1/", include("apps.work.urls")),
    path("api/v1/", include("apps.console.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
