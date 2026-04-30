"""Агрегаты рабочего дашборда (общий и internal-расширение)."""

from django.db.models import Count
from django.utils import timezone

from .models import WorkBoard, WorkCounterparty, WorkGroup, WorkTask
from .serializers import WorkBoardSerializer, WorkGroupSerializer, WorkTaskSerializer


def build_work_dashboard_data(user, request=None, *, internal_extra: bool = False) -> dict:
    """
    Данные для GET /work/dashboard/ и база для GET /internal/work/dashboard/.
    При internal_extra добавляются поля только для штатного контура.
    """
    ctx = {"request": request} if request is not None else {}
    groups_qs = WorkGroup.objects.filter(memberships__user=user).distinct()
    boards_qs = WorkBoard.objects.filter(group__in=groups_qs).distinct()
    due_qs = (
        WorkTask.objects.filter(board__in=boards_qs, due_date__gte=timezone.localdate())
        .order_by("due_date")[:10]
    )
    data: dict = {
        "tasks_due": WorkTaskSerializer(due_qs, many=True).data,
        "groups": WorkGroupSerializer(
            groups_qs.annotate(members_count=Count("memberships")),
            many=True,
            context=ctx,
        ).data,
        "boards": WorkBoardSerializer(boards_qs, many=True).data,
        "note": "Агрегаты рабочего контура.",
    }

    ek = getattr(user, "employment_kind", "") or ""
    if getattr(user, "is_employee", False):
        data["employment_scope"] = ek if ek in ("internal", "partner") else ""
    else:
        data["employment_scope"] = ""

    if getattr(user, "is_employee", False) and ek == "internal":
        data["internal_extension_available"] = True

    if internal_extra:
        open_tasks = (
            WorkTask.objects.filter(board__in=boards_qs)
            .exclude(column__semantic__in=["done", "released", "cancelled"])
            .count()
        )
        data["internal"] = {
            "open_tasks_estimate": open_tasks,
            "crm_readiness": {
                "stub_models_deployed": True,
                "counterparty_table_count": WorkCounterparty.objects.count(),
                "note": "Модели WorkCounterparty / WorkContact (задел CRM); связи с задачами — позже.",
            },
        }

    return data
