from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.console.permissions_catalog import PERMISSION_CATALOG

from .models import AdminAuditLog, Department, Organization, UserPermissionGroup
from .serializers import (
    AdminAuditLogSerializer,
    AdminUserSerializer,
    DepartmentSerializer,
    OrganizationSerializer,
    UserPermissionGroupSerializer,
)

User = get_user_model()


def _audit_json_payload(data: dict) -> dict:
    """Приводит validated_data к JSON-совместимому виду для AdminAuditLog."""
    out: dict = {}
    for k, v in data.items():
        if hasattr(v, "pk"):
            out[k] = v.pk
        elif isinstance(v, (list, tuple)) and v and hasattr(v[0], "pk"):
            out[k] = [x.pk for x in v]
        else:
            out[k] = v
    return out


class AdminUsersStubView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = (
            User.objects.order_by("id")
            .select_related("department", "department__organization")
            .prefetch_related("permission_groups")[:200]
        )
        return Response(AdminUserSerializer(qs, many=True).data)

    def patch(self, request):
        user_id = request.data.get("id")
        target = (
            User.objects.filter(pk=user_id)
            .select_related("department")
            .prefetch_related("permission_groups")
            .first()
        )
        if target is None:
            return Response({"detail": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
        serializer = AdminUserSerializer(target, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        AdminAuditLog.objects.create(
            actor=request.user,
            action="update_user_roles",
            target_user=target,
            payload=_audit_json_payload(dict(serializer.validated_data)),
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


class AdminPermissionCatalogView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response(PERMISSION_CATALOG)


class AdminPermissionGroupsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = UserPermissionGroup.objects.prefetch_related("members").order_by("name")
        return Response(UserPermissionGroupSerializer(qs, many=True).data)

    def post(self, request):
        ser = UserPermissionGroupSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        group = ser.save()
        AdminAuditLog.objects.create(
            actor=request.user,
            action="create_permission_group",
            target_user=None,
            payload={"group_id": group.id, "slug": group.slug},
        )
        return Response(UserPermissionGroupSerializer(group).data, status=status.HTTP_201_CREATED)


class AdminPermissionGroupDetailView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request, pk: int):
        group = UserPermissionGroup.objects.prefetch_related("members").filter(pk=pk).first()
        if group is None:
            return Response({"detail": "Не найдено."}, status=status.HTTP_404_NOT_FOUND)
        return Response(UserPermissionGroupSerializer(group).data)

    def patch(self, request, pk: int):
        group = UserPermissionGroup.objects.filter(pk=pk).first()
        if group is None:
            return Response({"detail": "Не найдено."}, status=status.HTTP_404_NOT_FOUND)
        ser = UserPermissionGroupSerializer(group, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ser.save()
        AdminAuditLog.objects.create(
            actor=request.user,
            action="update_permission_group",
            target_user=None,
            payload={"group_id": group.id},
        )
        return Response(UserPermissionGroupSerializer(group).data)

    def delete(self, request, pk: int):
        deleted, _ = UserPermissionGroup.objects.filter(pk=pk).delete()
        if not deleted:
            return Response({"detail": "Не найдено."}, status=status.HTTP_404_NOT_FOUND)
        AdminAuditLog.objects.create(
            actor=request.user,
            action="delete_permission_group",
            target_user=None,
            payload={"group_id": pk},
        )
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminOrganizationsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        qs = Organization.objects.all().order_by("name")
        return Response(OrganizationSerializer(qs, many=True).data)

    def post(self, request):
        ser = OrganizationSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        org = ser.save()
        AdminAuditLog.objects.create(
            actor=request.user,
            action="create_organization",
            target_user=None,
            payload={"organization_id": org.id},
        )
        return Response(OrganizationSerializer(org).data, status=status.HTTP_201_CREATED)


class AdminDepartmentsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        org_id = request.query_params.get("organization")
        qs = Department.objects.select_related("organization").order_by("name")
        if org_id:
            qs = qs.filter(organization_id=org_id)
        return Response(DepartmentSerializer(qs, many=True).data)

    def post(self, request):
        ser = DepartmentSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        dep = ser.save()
        AdminAuditLog.objects.create(
            actor=request.user,
            action="create_department",
            target_user=None,
            payload={"department_id": dep.id},
        )
        return Response(DepartmentSerializer(dep).data, status=status.HTTP_201_CREATED)
