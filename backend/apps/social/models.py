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

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="content_reports_sent",
    )
    target_type = models.CharField(max_length=32, choices=TargetType.choices)
    target_id = models.PositiveIntegerField()
    reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("target_type", "target_id")),
        ]
