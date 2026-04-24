from django.urls import path

from .views import AdminAuditLogsView, AdminRolesStubView, AdminUsersStubView

urlpatterns = [
    path("admin/users/", AdminUsersStubView.as_view(), name="admin-users"),
    path("admin/roles/", AdminRolesStubView.as_view(), name="admin-roles"),
    path("admin/audit/", AdminAuditLogsView.as_view(), name="admin-audit"),
]
