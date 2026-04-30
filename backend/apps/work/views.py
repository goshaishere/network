from django.db.models import Count
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsEmployeeOrStaff, RequiresPermissionSlug

from .board_columns import seed_columns_for_board
from .dashboard_data import build_work_dashboard_data
from .models import WorkBoard, WorkColumn, WorkGroup, WorkGroupMembership, WorkTask
from .services import broadcast_work_event
from .serializers import (
    WorkBoardSerializer,
    WorkColumnSerializer,
    WorkGroupSerializer,
    WorkTaskSerializer,
)


class WorkDashboardView(APIView):
    permission_classes = [IsEmployeeOrStaff, RequiresPermissionSlug]
    required_permission_slug_map = {"GET": "work.dashboard.read"}

    def get(self, request):
        return Response(build_work_dashboard_data(request.user, request, internal_extra=False))


class TasksGroupsView(APIView):
    permission_classes = [IsEmployeeOrStaff, RequiresPermissionSlug]
    required_permission_slug_map = {"GET": "work.group.read", "POST": "work.group.write"}

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
    permission_classes = [IsEmployeeOrStaff, RequiresPermissionSlug]
    required_permission_slug_map = {"GET": "work.board.read", "POST": "work.board.write"}

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
        seed_columns_for_board(board)
        return Response(WorkBoardSerializer(board).data, status=status.HTTP_201_CREATED)


class TasksColumnsView(APIView):
    permission_classes = [IsEmployeeOrStaff, RequiresPermissionSlug]
    required_permission_slug_map = {"GET": "work.column.read", "POST": "work.column.write"}

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
        broadcast_work_event(
            board_id=board.id,
            payload={"type": "column.created", "column": WorkColumnSerializer(col).data},
        )
        return Response(WorkColumnSerializer(col).data, status=status.HTTP_201_CREATED)


class TasksListCreateView(APIView):
    permission_classes = [IsEmployeeOrStaff, RequiresPermissionSlug]
    required_permission_slug_map = {"GET": "work.task.read", "POST": "work.task.write"}

    def get(self, request):
        board_id = request.query_params.get("board")
        qs = WorkTask.objects.filter(board__group__memberships__user=request.user).distinct()
        if board_id:
            qs = qs.filter(board_id=board_id)
        assignee_id = request.query_params.get("assignee")
        if assignee_id:
            qs = qs.filter(assignee_id=assignee_id)
        semantic = request.query_params.get("semantic")
        if semantic:
            qs = qs.filter(column__semantic=semantic)
        due_from = request.query_params.get("due_date_from")
        if due_from:
            qs = qs.filter(due_date__gte=due_from)
        due_to = request.query_params.get("due_date_to")
        if due_to:
            qs = qs.filter(due_date__lte=due_to)
        overdue = request.query_params.get("overdue")
        if overdue == "1":
            qs = qs.filter(due_date__lt=timezone.localdate())
        q = (request.query_params.get("q") or "").strip()
        if q:
            qs = qs.filter(title__icontains=q)
        ordering = request.query_params.get("ordering")
        if ordering in {"due_date", "-due_date", "created_at", "-created_at", "position", "-position"}:
            qs = qs.order_by(ordering, "id")
        return Response(WorkTaskSerializer(qs, many=True).data)

    def post(self, request):
        serializer = WorkTaskSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        board = serializer.validated_data["board"]
        if not WorkGroupMembership.objects.filter(group=board.group, user=request.user).exists():
            return Response({"detail": "Нет доступа к доске."}, status=status.HTTP_403_FORBIDDEN)
        task = serializer.save(created_by=request.user)
        broadcast_work_event(
            board_id=board.id,
            payload={"type": "task.created", "task": WorkTaskSerializer(task).data},
        )
        return Response(WorkTaskSerializer(task).data, status=status.HTTP_201_CREATED)


class TasksColumnsReorderView(APIView):
    """POST { board, order: [column_id, ...] } — позиции колонок на доске."""

    permission_classes = [IsEmployeeOrStaff, RequiresPermissionSlug]
    required_permission_slug_map = {"POST": "work.column.write"}

    def post(self, request):
        board_id = request.data.get("board")
        order = request.data.get("order")
        if board_id is None or not isinstance(order, list) or not order:
            return Response(
                {"detail": "Нужны поля board и order (непустой список id колонок)."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        board = (
            WorkBoard.objects.filter(
                pk=board_id,
                group__memberships__user=request.user,
            )
            .distinct()
            .first()
        )
        if board is None:
            return Response({"detail": "Доска не найдена."}, status=status.HTTP_404_NOT_FOUND)
        cols = list(WorkColumn.objects.filter(board=board))
        col_ids = {c.id for c in cols}
        try:
            order_ids = [int(x) for x in order]
        except (TypeError, ValueError):
            return Response({"detail": "order должен быть списком чисел."}, status=status.HTTP_400_BAD_REQUEST)
        if set(order_ids) != col_ids:
            return Response(
                {"detail": "Набор id колонок должен совпадать с колонками доски."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        for pos, col_id in enumerate(order_ids):
            WorkColumn.objects.filter(pk=col_id, board=board).update(position=pos)
        ordered = WorkColumn.objects.filter(board=board).order_by("position", "id")
        broadcast_work_event(
            board_id=board.id,
            payload={
                "type": "column.reordered",
                "board_id": board.id,
                "order": [c.id for c in ordered],
            },
        )
        return Response(WorkColumnSerializer(ordered, many=True).data)


class TasksDetailView(APIView):
    permission_classes = [IsEmployeeOrStaff, RequiresPermissionSlug]
    required_permission_slug_map = {"PATCH": "work.task.write"}

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
        broadcast_work_event(
            board_id=task.board_id,
            payload={"type": "task.updated", "task": serializer.data},
        )
        return Response(serializer.data)
