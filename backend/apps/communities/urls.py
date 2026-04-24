from django.urls import path

from .views import (
    CommunityDetailView,
    CommunityJoinView,
    CommunityListCreateView,
    CommunityPostListCreateView,
)

urlpatterns = [
    path("communities/", CommunityListCreateView.as_view(), name="communities-list"),
    path("communities/<slug:slug>/", CommunityDetailView.as_view(), name="communities-detail"),
    path("communities/<slug:slug>/join/", CommunityJoinView.as_view(), name="communities-join"),
    path(
        "communities/<slug:slug>/posts/",
        CommunityPostListCreateView.as_view(),
        name="communities-posts",
    ),
]
