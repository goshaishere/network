from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class WorkGroup(models.Model):
    name = models.CharField(_("название"), max_length=160)
    slug = models.SlugField(_("slug"), max_length=80, unique=True, db_index=True)
    description = models.TextField(_("описание"), blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="work_groups_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        verbose_name = _("рабочая группа")
        verbose_name_plural = _("рабочие группы")

    def __str__(self) -> str:
        return self.name


class WorkGroupMembership(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", _("Владелец")
        MEMBER = "member", _("Участник")

    group = models.ForeignKey(WorkGroup, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="work_memberships"
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("group", "user")


class WorkBoard(models.Model):
    class Preset(models.TextChoices):
        GENERIC_PM = "generic_pm", _("Generic PM")
        IT_SDLC = "it_sdlc", _("IT SDLC")
        CUSTOM = "custom", _("Custom")

    group = models.ForeignKey(WorkGroup, on_delete=models.CASCADE, related_name="boards")
    name = models.CharField(_("название"), max_length=160)
    preset = models.CharField(max_length=20, choices=Preset.choices, default=Preset.GENERIC_PM)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("id",)
        verbose_name = _("доска")
        verbose_name_plural = _("доски")


class WorkColumn(models.Model):
    class Semantic(models.TextChoices):
        PLANNED = "planned", _("Запланировано")
        IN_PROGRESS = "in_progress", _("В работе")
        REVIEW = "review", _("Проверка")
        DONE = "done", _("Сделано")
        RELEASED = "released", _("Релиз")
        CANCELLED = "cancelled", _("Отменено")
        BACKLOG = "backlog", _("Бэклог")

    board = models.ForeignKey(WorkBoard, on_delete=models.CASCADE, related_name="columns")
    title = models.CharField(max_length=120)
    semantic = models.CharField(max_length=30, choices=Semantic.choices, blank=True, default="")
    position = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("position", "id")


class WorkTask(models.Model):
    board = models.ForeignKey(WorkBoard, on_delete=models.CASCADE, related_name="tasks")
    column = models.ForeignKey(WorkColumn, on_delete=models.CASCADE, related_name="tasks")
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="work_tasks_assigned",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="work_tasks_created",
    )
    due_date = models.DateField(null=True, blank=True)
    position = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("position", "id")
