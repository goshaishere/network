from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class WallPost(models.Model):
    wall_owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wall_posts_received",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wall_posts_authored",
    )
    body = models.TextField(_("текст"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = _("пост на стене")
        verbose_name_plural = _("посты на стенах")
