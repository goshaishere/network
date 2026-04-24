from django.urls import path

from .views import ConversationListCreateView, MessageListCreateView

urlpatterns = [
    path(
        "messaging/conversations/",
        ConversationListCreateView.as_view(),
        name="messaging-conversations",
    ),
    path(
        "messaging/conversations/<int:pk>/messages/",
        MessageListCreateView.as_view(),
        name="messaging-messages",
    ),
]
