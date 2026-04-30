from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import RequiresPermissionSlug

from .feed import build_feed_page
from .models import FriendRequest
from .serializers import (
    ContentReportCreateSerializer,
    FriendRequestCreateSerializer,
    FriendRequestSerializer,
    UserMiniSerializer,
)

User = get_user_model()


class FeedView(APIView):
    permission_classes = [IsAuthenticated, RequiresPermissionSlug]
    required_permission_slug_map = {"GET": "social.read"}

    def get(self, request):
        try:
            offset = int(request.query_params.get("offset", "0"))
        except ValueError:
            offset = 0
        results, next_offset = build_feed_page(request.user, offset=offset, request=request)
        return Response({"results": results, "next_offset": next_offset})


class FriendsListView(APIView):
    permission_classes = [IsAuthenticated, RequiresPermissionSlug]
    required_permission_slug_map = {"GET": "social.read"}

    def get(self, request):
        u = request.user
        rows = (
            FriendRequest.objects.filter(
                status=FriendRequest.Status.ACCEPTED,
            )
            .filter(Q(from_user=u) | Q(to_user=u))
            .select_related("from_user", "to_user")
        )
        others = []
        seen: set[int] = set()
        for r in rows:
            other = r.to_user if r.from_user_id == u.id else r.from_user
            if other.id not in seen:
                seen.add(other.id)
                others.append(other)
        return Response(UserMiniSerializer(others, many=True).data)


class FriendRequestCreateView(APIView):
    permission_classes = [IsAuthenticated, RequiresPermissionSlug]
    required_permission_slug_map = {"POST": "social.write"}

    def post(self, request):
        ser = FriendRequestCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        to_id = ser.validated_data["to_user_id"]
        if to_id == request.user.id:
            return Response({"detail": "Нельзя отправить запрос самому себе."}, status=status.HTTP_400_BAD_REQUEST)
        target = User.objects.filter(pk=to_id).first()
        if target is None:
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
        rev = FriendRequest.objects.filter(from_user=target, to_user=request.user).first()
        if rev and rev.status == FriendRequest.Status.PENDING:
            rev.status = FriendRequest.Status.ACCEPTED
            rev.save(update_fields=["status"])
            return Response(FriendRequestSerializer(rev).data, status=status.HTTP_200_OK)
        fr, created = FriendRequest.objects.get_or_create(
            from_user=request.user,
            to_user=target,
            defaults={"status": FriendRequest.Status.PENDING},
        )
        if not created and fr.status != FriendRequest.Status.PENDING:
            return Response(
                {"detail": "Запрос уже обработан."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(FriendRequestSerializer(fr).data, status=status.HTTP_201_CREATED)


class FriendRequestIncomingView(APIView):
    permission_classes = [IsAuthenticated, RequiresPermissionSlug]
    required_permission_slug_map = {"GET": "social.read"}

    def get(self, request):
        qs = FriendRequest.objects.filter(
            to_user=request.user,
            status=FriendRequest.Status.PENDING,
        ).select_related("from_user", "to_user")
        return Response(FriendRequestSerializer(qs, many=True).data)


class FriendRequestAcceptView(APIView):
    permission_classes = [IsAuthenticated, RequiresPermissionSlug]
    required_permission_slug_map = {"POST": "social.write"}

    def post(self, request, pk: int):
        fr = FriendRequest.objects.filter(pk=pk, to_user=request.user).first()
        if fr is None:
            return Response({"detail": "Не найдено."}, status=status.HTTP_404_NOT_FOUND)
        if fr.status != FriendRequest.Status.PENDING:
            return Response({"detail": "Уже обработано."}, status=status.HTTP_400_BAD_REQUEST)
        fr.status = FriendRequest.Status.ACCEPTED
        fr.save(update_fields=["status"])
        return Response(FriendRequestSerializer(fr).data)


class FriendRequestRejectView(APIView):
    permission_classes = [IsAuthenticated, RequiresPermissionSlug]
    required_permission_slug_map = {"POST": "social.write"}

    def post(self, request, pk: int):
        fr = FriendRequest.objects.filter(pk=pk, to_user=request.user).first()
        if fr is None:
            return Response({"detail": "Не найдено."}, status=status.HTTP_404_NOT_FOUND)
        if fr.status != FriendRequest.Status.PENDING:
            return Response({"detail": "Уже обработано."}, status=status.HTTP_400_BAD_REQUEST)
        fr.status = FriendRequest.Status.REJECTED
        fr.save(update_fields=["status"])
        return Response(FriendRequestSerializer(fr).data)


class ContentReportCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, RequiresPermissionSlug]
    required_permission_slug_map = {"POST": "moderation.report.write"}
    serializer_class = ContentReportCreateSerializer
