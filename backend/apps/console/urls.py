from django.urls import path

from .views import (
    AdminAuditLogsView,
    AdminDepartmentsView,
    AdminOrganizationsView,
    AdminPermissionCatalogView,
    AdminPermissionGroupDetailView,
    AdminPermissionGroupsView,
    AdminRolesStubView,
    AdminUsersStubView,
)

urlpatterns = [
    path("admin/users/", AdminUsersStubView.as_view(), name="admin-users"),
    path("admin/roles/", AdminRolesStubView.as_view(), name="admin-roles"),
    path("admin/audit/", AdminAuditLogsView.as_view(), name="admin-audit"),
    path(
        "admin/permission-catalog/",
        AdminPermissionCatalogView.as_view(),
        name="admin-permission-catalog",
    ),
    path(
        "admin/permission-groups/",
        AdminPermissionGroupsView.as_view(),
        name="admin-permission-groups",
    ),
    path(
        "admin/permission-groups/<int:pk>/",
        AdminPermissionGroupDetailView.as_view(),
        name="admin-permission-group-detail",
    ),
    path(
        "admin/organizations/",
        AdminOrganizationsView.as_view(),
        name="admin-organizations",
    ),
    path(
        "admin/departments/",
        AdminDepartmentsView.as_view(),
        name="admin-departments",
    ),
]
