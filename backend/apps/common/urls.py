from django.urls import path

from .views import HealthView, InternalStatusView

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("internal/status/", InternalStatusView.as_view(), name="internal-status"),
]
