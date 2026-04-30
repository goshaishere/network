from django.urls import path

from .views import (
    AdminAuditLogsView,
    AdminCommunitiesListView,
    AdminCommunityDetailView,
    AdminCommunityPostDeleteView,
    AdminCommunityPostsView,
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
    path("admin/communities/", AdminCommunitiesListView.as_view(), name="admin-communities"),
    path(
        "admin/communities/posts/<int:pk>/",
        AdminCommunityPostDeleteView.as_view(),
        name="admin-community-post-delete",
    ),
    path(
        "admin/communities/<int:pk>/posts/",
        AdminCommunityPostsView.as_view(),
        name="admin-community-posts",
    ),
    path(
        "admin/communities/<int:pk>/",
        AdminCommunityDetailView.as_view(),
        name="admin-community-detail",
    ),
]
