from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    class Kind(models.TextChoices):
        DIRECT = "direct", _("Личный")
        GROUP = "group", _("Группа")

    kind = models.CharField(max_length=10, choices=Kind.choices, default=Kind.DIRECT)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="conversations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField(_("текст"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-id",)
