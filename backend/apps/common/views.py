from django.contrib.auth import get_user_model
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.views import View
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsInternalEmployeeOrStaff

User = get_user_model()


class HealthView(View):
    """GET /api/v1/health/ — проверка процесса и БД."""

    def get(self, request):
        db_ok = True
        try:
            connection.ensure_connection()
        except Exception:
            db_ok = False
        status = 200 if db_ok else 503
        return JsonResponse(
            {"status": "ok" if db_ok else "degraded", "database": "up" if db_ok else "down"},
            status=status,
        )


class InternalStatusView(APIView):
    permission_classes = [IsInternalEmployeeOrStaff]

    def get(self, request):
        return Response({"status": "ok", "scope": "internal", "user_id": request.user.id})


class PrometheusMetricsView(APIView):
    """Минимальные метрики в формате Prometheus (для scrape внутри периметра)."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        n_users = User.objects.count()
        body = (
            "# HELP network_users_total Number of user accounts\n"
            "# TYPE network_users_total gauge\n"
            f"network_users_total {n_users}\n"
        )
        return HttpResponse(body, content_type="text/plain; version=0.0.4")
