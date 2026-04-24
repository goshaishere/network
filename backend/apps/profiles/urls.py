from django.urls import path

from .views import DashboardLayoutView, ProfileDetailView, ProfileMeView

urlpatterns = [
    path("profiles/me/", ProfileMeView.as_view(), name="profiles-me"),
    path("profiles/me/dashboard/", DashboardLayoutView.as_view(), name="profiles-me-dashboard"),
    path("profiles/<int:user_id>/", ProfileDetailView.as_view(), name="profiles-detail"),
]
