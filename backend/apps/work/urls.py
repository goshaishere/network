from django.urls import path

from .views import (
    TasksBoardsView,
    TasksColumnsView,
    TasksDetailView,
    TasksGroupsView,
    TasksListCreateView,
    WorkDashboardView,
)

urlpatterns = [
    path("work/dashboard/", WorkDashboardView.as_view(), name="work-dashboard"),
    path("tasks/groups/", TasksGroupsView.as_view(), name="tasks-groups"),
    path("tasks/boards/", TasksBoardsView.as_view(), name="tasks-boards"),
    path("tasks/columns/", TasksColumnsView.as_view(), name="tasks-columns"),
    path("tasks/", TasksListCreateView.as_view(), name="tasks"),
    path("tasks/<int:pk>/", TasksDetailView.as_view(), name="task-detail"),
]
