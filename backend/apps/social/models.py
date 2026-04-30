from django.conf import settings
from django.db import models


class FriendRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает"
        ACCEPTED = "accepted", "Принято"
        REJECTED = "rejected", "Отклонено"

    from_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friend_requests_sent",
    )
    to_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="friend_requests_received",
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["from_user", "to_user"], name="social_unique_friend_request")
        ]
        ordering = ("-created_at",)


class ContentReport(models.Model):
    """Жалоба на пост (модерация ленты / контента)."""

    class TargetType(models.TextChoices):
        WALL_POST = "wall_post", "Пост на стене"
        COMMUNITY_POST = "community_post", "Пост в сообществе"

    class Status(models.TextChoices):
        NEW = "new", "Новая"
        IN_REVIEW = "in_review", "В работе"
        RESOLVED = "resolved", "Решена"
        REJECTED = "rejected", "Отклонена"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="content_reports_sent",
    )
    target_type = models.CharField(max_length=32, choices=TargetType.choices)
    target_id = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_reports_assigned",
    )
    decision = models.CharField(max_length=64, blank=True, default="")
    resolution_note = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="content_reports_resolved",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("target_type", "target_id")),
        ]
