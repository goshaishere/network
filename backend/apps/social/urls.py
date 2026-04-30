from django.urls import path

from .views import (
    FeedView,
    FriendRequestAcceptView,
    FriendRequestCreateView,
    FriendRequestIncomingView,
    FriendRequestRejectView,
    FriendsListView,
)

urlpatterns = [
    path("social/feed/", FeedView.as_view(), name="social-feed"),
    path("social/friends/", FriendsListView.as_view(), name="social-friends"),
    path("social/friend-requests/", FriendRequestCreateView.as_view(), name="social-friend-requests"),
    path(
        "social/friend-requests/incoming/",
        FriendRequestIncomingView.as_view(),
        name="social-friend-requests-incoming",
    ),
    path(
        "social/friend-requests/<int:pk>/accept/",
        FriendRequestAcceptView.as_view(),
        name="social-friend-request-accept",
    ),
    path(
        "social/friend-requests/<int:pk>/reject/",
        FriendRequestRejectView.as_view(),
        name="social-friend-request-reject",
    ),
]
