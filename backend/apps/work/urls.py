from django.urls import path

from .views import TasksBoardsStubView, TasksGroupsStubView, WorkDashboardView

urlpatterns = [
    path("work/dashboard/", WorkDashboardView.as_view(), name="work-dashboard"),
    path("tasks/groups/", TasksGroupsStubView.as_view(), name="tasks-groups"),
    path("tasks/boards/", TasksBoardsStubView.as_view(), name="tasks-boards"),
]
