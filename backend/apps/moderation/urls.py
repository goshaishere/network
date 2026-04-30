from django.urls import path

from .views import ModerationReportDetailView, ModerationReportsView

urlpatterns = [
    path("admin/moderation/reports/", ModerationReportsView.as_view(), name="moderation-reports"),
    path(
        "admin/moderation/reports/<int:pk>/",
        ModerationReportDetailView.as_view(),
        name="moderation-report-detail",
    ),
]
