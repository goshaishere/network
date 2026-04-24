from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsEmployeeOrStaff

from .models import WorkBoard, WorkColumn, WorkGroup, WorkGroupMembership, WorkTask
from .serializers import (
    WorkBoardSerializer,
    WorkColumnSerializer,
    WorkGroupSerializer,
    WorkTaskSerializer,
)


class WorkDashboardView(APIView):
    permission_classes = [IsEmployeeOrStaff]

    def get(self, request):
        groups_qs = WorkGroup.objects.filter(memberships__user=request.user).distinct()
        boards_qs = WorkBoard.objects.filter(group__in=groups_qs).distinct()
        due_qs = (
            WorkTask.objects.filter(board__in=boards_qs, due_date__gte=timezone.localdate())
            .order_by("due_date")[:10]
        )
        return Response(
            {
                "tasks_due": WorkTaskSerializer(due_qs, many=True).data,
                "groups": WorkGroupSerializer(
                    groups_qs.annotate(members_count=Count("memberships")),
                    many=True,
                    context={"request": request},
                ).data,
                "boards": WorkBoardSerializer(boards_qs, many=True).data,
                "note": "Агрегаты рабочего контура.",
            }
        )


class TasksGroupsView(APIView):
    permission_classes = [IsEmployeeOrStaff]

    def get(self, request):
        groups = (
            WorkGroup.objects.filter(memberships__user=request.user)
            .annotate(members_count=Count("memberships"))
            .distinct()
        )
        return Response(WorkGroupSerializer(groups, many=True, context={"request": request}).data)

    def post(self, request):
        serializer = WorkGroupSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        group = serializer.save(created_by=request.user)
        WorkGroupMembership.objects.get_or_create(
            group=group, user=request.user, defaults={"role": WorkGroupMembership.Role.OWNER}
        )
        return Response(
            WorkGroupSerializer(group, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class TasksBoardsView(APIView):
    permission_classes = [IsEmployeeOrStaff]

    def get(self, request):
        group_id = request.query_params.get("group")
        boards = WorkBoard.objects.filter(group__memberships__user=request.user)
        if group_id:
            boards = boards.filter(group_id=group_id)
        return Response(WorkBoardSerializer(boards.distinct(), many=True).data)

    def post(self, request):
        serializer = WorkBoardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = serializer.validated_data["group"]
        if not WorkGroupMembership.objects.filter(group=group, user=request.user).exists():
            return Response({"detail": "Нет доступа к группе."}, status=status.HTTP_403_FORBIDDEN)
        board = serializer.save()
        if board.preset == WorkBoard.Preset.GENERIC_PM:
            WorkColumn.objects.bulk_create(
                [
                    WorkColumn(board=board, title="Planned", semantic="planned", position=0),
                    WorkColumn(
                        board=board,
                        title="In Progress",
                        semantic="in_progress",
                        position=1,
                    ),
                    WorkColumn(board=board, title="Review", semantic="review", position=2),
                    WorkColumn(board=board, title="Done", semantic="done", position=3),
                    WorkColumn(board=board, title="Released", semantic="released", position=4),
                    WorkColumn(board=board, title="Cancelled", semantic="cancelled", position=5),
                ]
            )
        elif board.preset == WorkBoard.Preset.IT_SDLC:
            WorkColumn.objects.bulk_create(
                [
                    WorkColumn(board=board, title="Backlog", semantic="backlog", position=0),
                    WorkColumn(
                        board=board,
                        title="In Progress",
                        semantic="in_progress",
                        position=1,
                    ),
                    WorkColumn(board=board, title="Review", semantic="review", position=2),
                    WorkColumn(board=board, title="Released", semantic="released", position=3),
                ]
            )
        return Response(WorkBoardSerializer(board).data, status=status.HTTP_201_CREATED)


class TasksColumnsView(APIView):
    permission_classes = [IsEmployeeOrStaff]

    def get(self, request):
        board_id = request.query_params.get("board")
        columns = WorkColumn.objects.filter(board__group__memberships__user=request.user)
        if board_id:
            columns = columns.filter(board_id=board_id)
        return Response(WorkColumnSerializer(columns.distinct(), many=True).data)

    def post(self, request):
        serializer = WorkColumnSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.validated_data["board"]
        if not WorkGroupMembership.objects.filter(group=board.group, user=request.user).exists():
            return Response({"detail": "Нет доступа к доске."}, status=status.HTTP_403_FORBIDDEN)
        col = serializer.save()
        return Response(WorkColumnSerializer(col).data, status=status.HTTP_201_CREATED)


class TasksListCreateView(APIView):
    permission_classes = [IsEmployeeOrStaff]

    def get(self, request):
        board_id = request.query_params.get("board")
        qs = WorkTask.objects.filter(board__group__memberships__user=request.user).distinct()
        if board_id:
            qs = qs.filter(board_id=board_id)
        return Response(WorkTaskSerializer(qs, many=True).data)

    def post(self, request):
        serializer = WorkTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.validated_data["board"]
        if not WorkGroupMembership.objects.filter(group=board.group, user=request.user).exists():
            return Response({"detail": "Нет доступа к доске."}, status=status.HTTP_403_FORBIDDEN)
        task = serializer.save(created_by=request.user)
        return Response(WorkTaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TasksDetailView(APIView):
    permission_classes = [IsEmployeeOrStaff]

    def patch(self, request, pk: int):
        task = (
            WorkTask.objects.filter(
                pk=pk,
                board__group__memberships__user=request.user,
            )
            .distinct()
            .first()
        )
        if task is None:
            return Response({"detail": "Не найдено."}, status=status.HTTP_404_NOT_FOUND)
        serializer = WorkTaskSerializer(task, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
