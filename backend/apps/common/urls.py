from django.urls import path

from .views import (
    HealthView,
    InternalStatusView,
    InternalWorkDashboardView,
    LiveHealthView,
    PrometheusMetricsView,
    ReadyHealthView,
)

urlpatterns = [
    path("health/live/", LiveHealthView.as_view(), name="health-live"),
    path("health/ready/", ReadyHealthView.as_view(), name="health-ready"),
    path("health/", HealthView.as_view(), name="health"),
    path("internal/status/", InternalStatusView.as_view(), name="internal-status"),
    path(
        "internal/work/dashboard/",
        InternalWorkDashboardView.as_view(),
        name="internal-work-dashboard",
    ),
    path("metrics/", PrometheusMetricsView.as_view(), name="prometheus-metrics"),
]
