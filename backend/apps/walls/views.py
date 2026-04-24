from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from apps.common.pagination import SmallPagePagination
from apps.common.permissions import IsOwnerOrReadOnly
from apps.profiles.models import Profile

from .models import WallPost
from .serializers import WallPostSerializer

User = get_user_model()


class WallPostListCreateView(generics.ListCreateAPIView):
    serializer_class = WallPostSerializer
    pagination_class = SmallPagePagination

    def get_queryset(self):
        uid = self.kwargs["user_id"]
        return WallPost.objects.filter(wall_owner_id=uid).select_related("author", "wall_owner")

    def list(self, request, *args, **kwargs):
        owner = get_object_or_404(User, pk=kwargs["user_id"])
        try:
            prof = owner.profile
        except Profile.DoesNotExist:
            prof = None
        if prof and prof.privacy == Profile.Privacy.PRIVATE:
            if not request.user.is_authenticated or request.user.id != owner.id:
                return Response({"detail": "Стена недоступна."}, status=status.HTTP_404_NOT_FOUND)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied()
        wall_owner = get_object_or_404(User, pk=self.kwargs["user_id"])
        serializer.save(author=self.request.user, wall_owner=wall_owner)


class WallPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = WallPostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    lookup_field = "pk"

    def get_permissions(self):
        if self.request.method in ("PATCH", "DELETE", "PUT"):
            return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]
        return super().get_permissions()

    def get_queryset(self):
        return WallPost.objects.select_related("author", "wall_owner")
