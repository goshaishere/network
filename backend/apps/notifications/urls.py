from django.urls import path

from .views import NotificationListView, NotificationReadAllView, NotificationReadView

urlpatterns = [
    path("notifications/", NotificationListView.as_view(), name="notifications-list"),
    path("notifications/<int:pk>/read/", NotificationReadView.as_view(), name="notifications-read"),
    path("notifications/read-all/", NotificationReadAllView.as_view(), name="notifications-read-all"),
]
