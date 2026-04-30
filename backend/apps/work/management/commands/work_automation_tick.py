from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.work.models import WorkTask
from apps.work.services import broadcast_work_event


class Command(BaseCommand):
    help = "MVP automation: детект просроченных задач и публикация событий."

    def handle(self, *args, **options):
        today = timezone.localdate()
        overdue_qs = WorkTask.objects.filter(due_date__lt=today).exclude(column__semantic="done")
        count = 0
        for task in overdue_qs.select_related("board"):
            broadcast_work_event(
                board_id=task.board_id,
                payload={"type": "task.overdue", "task_id": task.id, "due_date": str(task.due_date)},
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"work_automation_tick: overdue events={count}"))
