from django.http import HttpResponse, JsonResponse
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.health_checks import is_ready, overall_health_status
from apps.common.metrics_export import render_prometheus_metrics
from apps.common.permissions import CanScrapeMetrics, IsInternalEmployeeOrStaff
from apps.work.dashboard_data import build_work_dashboard_data


class HealthView(View):
    """GET /api/v1/health/ — БД, Redis (если нужен), диск, версия."""

    def get(self, request):
        payload, code = overall_health_status()
        return JsonResponse(payload, status=code)


class LiveHealthView(View):
    """GET /api/v1/health/live/ — только «процесс отвечает» (liveness)."""

    def get(self, request):
        return JsonResponse({"status": "alive"})


class ReadyHealthView(View):
    """GET /api/v1/health/ready/ — готовность принимать трафик (readiness)."""

    def get(self, request):
        if is_ready():
            return JsonResponse({"status": "ready"})
        return JsonResponse({"status": "not_ready"}, status=503)


class InternalStatusView(APIView):
    permission_classes = [IsInternalEmployeeOrStaff]

    def get(self, request):
        return Response({"status": "ok", "scope": "internal", "user_id": request.user.id})


class InternalWorkDashboardView(APIView):
    """
    Расширенный рабочий дашборд только для штата (internal) или staff.
    Партнёр получает 403 — не подменяет общий /work/dashboard/.
    """

    permission_classes = [IsInternalEmployeeOrStaff]

    def get(self, request):
        data = build_work_dashboard_data(request.user, request, internal_extra=True)
        data["scope"] = "internal_api"
        return Response(data)


class PrometheusMetricsView(APIView):
    """GET /api/v1/metrics/ — формат Prometheus."""

    authentication_classes = []
    permission_classes = [CanScrapeMetrics]

    def get(self, request):
        body, ctype = render_prometheus_metrics()
        return HttpResponse(body, content_type=ctype)
