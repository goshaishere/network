from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import SmallPagePagination

from .models import Community, CommunityMembership, CommunityPost
from .serializers import (
    CommunityDetailSerializer,
    CommunityListSerializer,
    CommunityPostSerializer,
)


def _is_moderator(user, community):
    if not user.is_authenticated:
        return False
    m = CommunityMembership.objects.filter(community=community, user=user).first()
    return bool(m and m.role == CommunityMembership.Role.MODERATOR)


def _is_member(user, community):
    if not user.is_authenticated:
        return False
    return CommunityMembership.objects.filter(community=community, user=user).exists()


class CommunityListCreateView(generics.ListCreateAPIView):
    queryset = (
        Community.objects.annotate(members_count=Count("memberships", distinct=True))
        .order_by("-created_at")
    )
    pagination_class = SmallPagePagination

    def get_serializer_class(self):
        if self.request.method == "POST":
            return CommunityDetailSerializer
        return CommunityListSerializer

    def perform_create(self, serializer):
        if not self.request.user.is_authenticated:
            raise PermissionDenied()
        c = serializer.save(creator=self.request.user)
        CommunityMembership.objects.create(
            community=c,
            user=self.request.user,
            role=CommunityMembership.Role.MODERATOR,
        )


class CommunityDetailView(generics.RetrieveUpdateAPIView):
    queryset = Community.objects.all()
    lookup_field = "slug"

    def get_serializer_class(self):
        return CommunityDetailSerializer

    def perform_update(self, serializer):
        community = self.get_object()
        u = self.request.user
        if not u.is_authenticated:
            raise PermissionDenied()
        if not (_is_moderator(u, community) or community.creator_id == u.id):
            raise PermissionDenied()
        serializer.save()


class CommunityJoinView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, slug):
        community = get_object_or_404(Community, slug=slug)
        if not community.is_open and not _is_moderator(request.user, community):
            raise PermissionDenied("Закрытое сообщество.")
        CommunityMembership.objects.get_or_create(
            community=community,
            user=request.user,
            defaults={"role": CommunityMembership.Role.MEMBER},
        )
        return Response({"detail": "ok"}, status=status.HTTP_200_OK)


class CommunityPostListCreateView(generics.ListCreateAPIView):
    serializer_class = CommunityPostSerializer
    pagination_class = SmallPagePagination

    def get_queryset(self):
        slug = self.kwargs["slug"]
        return CommunityPost.objects.filter(community__slug=slug).select_related(
            "author", "community"
        )

    def list(self, request, *args, **kwargs):
        community = get_object_or_404(Community, slug=kwargs["slug"])
        if not community.is_open and not _is_member(request.user, community):
            return Response({"detail": "Нет доступа."}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        community = get_object_or_404(Community, slug=self.kwargs["slug"])
        if not _is_member(self.request.user, community):
            raise PermissionDenied("Нужно вступить в сообщество.")
        serializer.save(community=community, author=self.request.user)
