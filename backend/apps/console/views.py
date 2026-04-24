from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AdminAuditLog
from .serializers import AdminAuditLogSerializer, AdminUserSerializer

User = get_user_model()


class AdminUsersStubView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = User.objects.order_by("id")[:50]
        return Response(AdminUserSerializer(qs, many=True).data)

    def patch(self, request):
        user_id = request.data.get("id")
        target = User.objects.filter(pk=user_id).first()
        if target is None:
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdminUserSerializer(target, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        AdminAuditLog.objects.create(
            actor=request.user,
            action="update_user_roles",
            target_user=target,
            payload=serializer.validated_data,
        )
        return Response(AdminUserSerializer(target).data)


class AdminRolesStubView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(
            [
                {"slug": "user", "name": "Пользователь"},
                {"slug": "employee", "name": "Сотрудник"},
                {"slug": "admin", "name": "Администратор"},
            ]
        )


class AdminAuditLogsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        logs = AdminAuditLog.objects.select_related("actor", "target_user").all()[:100]
        return Response(AdminAuditLogSerializer(logs, many=True).data)
