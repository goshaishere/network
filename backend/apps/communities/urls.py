from django.urls import path

from .views import (
    CommunityDetailView,
    CommunityJoinView,
    CommunityListCreateView,
    CommunityMineListView,
    CommunityPostDetailView,
    CommunityPostListCreateView,
)

urlpatterns = [
    path("communities/mine/", CommunityMineListView.as_view(), name="communities-mine"),
    path("communities/", CommunityListCreateView.as_view(), name="communities-list"),
    path("communities/<slug:slug>/", CommunityDetailView.as_view(), name="communities-detail"),
    path("communities/<slug:slug>/join/", CommunityJoinView.as_view(), name="communities-join"),
    path(
        "communities/<slug:slug>/posts/<int:pk>/",
        CommunityPostDetailView.as_view(),
        name="communities-post-detail",
    ),
    path(
        "communities/<slug:slug>/posts/",
        CommunityPostListCreateView.as_view(),
        name="communities-posts",
    ),
]
