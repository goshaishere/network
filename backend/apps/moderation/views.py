from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import RequiresPermissionSlug
from apps.social.models import ContentReport

from .serializers import ModerationReportSerializer


class ModerationReportsView(APIView):
    permission_classes = [IsAdminUser, RequiresPermissionSlug]
    required_permission_slug_map = {"GET": "moderation.queue.read"}

    def get(self, request):
        qs = ContentReport.objects.select_related("reporter", "assigned_to", "resolved_by").order_by("-created_at")
        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response(ModerationReportSerializer(qs[:200], many=True).data)


class ModerationReportDetailView(APIView):
    permission_classes = [IsAdminUser, RequiresPermissionSlug]
    required_permission_slug_map = {
        "GET": "moderation.queue.read",
        "PATCH": "moderation.queue.write",
    }

    def get(self, request, pk: int):
        report = ContentReport.objects.filter(pk=pk).first()
        if report is None:
            return Response({"detail": "Не найдено."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ModerationReportSerializer(report).data)

    def patch(self, request, pk: int):
        report = ContentReport.objects.filter(pk=pk).first()
        if report is None:
            return Response({"detail": "Не найдено."}, status=status.HTTP_404_NOT_FOUND)
        serializer = ModerationReportSerializer(report, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        if instance.status in {ContentReport.Status.RESOLVED, ContentReport.Status.REJECTED}:
            instance.resolved_at = timezone.now()
            instance.resolved_by = request.user
            instance.save(update_fields=["resolved_at", "resolved_by"])
            send_mail(
                subject=f"Moderation report #{instance.id} resolved",
                message=f"Report {instance.id} status: {instance.status}, decision: {instance.decision}",
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "network@localhost"),
                recipient_list=[request.user.email] if request.user.email else [],
                fail_silently=True,
            )
        return Response(ModerationReportSerializer(instance).data)
