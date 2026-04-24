from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class WorkDashboardView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "tasks_due": [],
                "groups": [],
                "boards": [],
                "note": "Заглушка: агрегаты /work по ROLES-AND-TASKS — в следующих итерациях.",
            }
        )


class TasksGroupsStubView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([])


class TasksBoardsStubView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([])
