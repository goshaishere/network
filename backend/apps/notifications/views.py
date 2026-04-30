from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import RequiresPermissionSlug

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    permission_classes = [IsAuthenticated, RequiresPermissionSlug]
    required_permission_slug_map = {"GET": "notifications.read"}

    def get(self, request):
        qs = Notification.objects.filter(user=request.user).order_by("is_read", "-created_at")
        return Response(NotificationSerializer(qs[:200], many=True).data)


class NotificationReadView(APIView):
    permission_classes = [IsAuthenticated, RequiresPermissionSlug]
    required_permission_slug_map = {"POST": "notifications.write"}

    def post(self, request, pk: int):
        notification = Notification.objects.filter(pk=pk, user=request.user).first()
        if notification is None:
            return Response({"detail": "Не найдено."}, status=404)
        if not notification.is_read:
            notification.is_read = True
            notification.read_at = timezone.now()
            notification.save(update_fields=["is_read", "read_at"])
        return Response(NotificationSerializer(notification).data)


class NotificationReadAllView(APIView):
    permission_classes = [IsAuthenticated, RequiresPermissionSlug]
    required_permission_slug_map = {"POST": "notifications.write"}

    def post(self, request):
        unread = Notification.objects.filter(user=request.user, is_read=False)
        unread.update(is_read=True, read_at=timezone.now())
        return Response({"detail": "ok"})
