from django.urls import path

from .views import AdminRolesStubView, AdminUsersStubView

urlpatterns = [
    path("admin/users/", AdminUsersStubView.as_view(), name="admin-users"),
    path("admin/roles/", AdminRolesStubView.as_view(), name="admin-roles"),
]
