from django.db import connection
from django.http import JsonResponse
from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsInternalEmployeeOrStaff


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
