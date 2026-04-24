from django.urls import path

from .views import WallPostDetailView, WallPostListCreateView

urlpatterns = [
    path("walls/<int:user_id>/posts/", WallPostListCreateView.as_view(), name="walls-posts"),
    path("walls/posts/<int:pk>/", WallPostDetailView.as_view(), name="walls-post-detail"),
]
