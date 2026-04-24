from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Profile(models.Model):
    class Privacy(models.TextChoices):
        PUBLIC = "public", _("Публичный")
        PRIVATE = "private", _("Только я")

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.TextField(_("о себе"), blank=True)
    avatar = models.URLField(_("аватар URL"), blank=True)
    locale = models.CharField(_("локаль"), max_length=10, default="ru")
    privacy = models.CharField(
        _("приватность"),
        max_length=20,
        choices=Privacy.choices,
        default=Privacy.PUBLIC,
    )
    dashboard_layout = models.JSONField(_("раскладка дашборда"), default=dict, blank=True)
    default_landing = models.CharField(_("лендинг по умолчанию"), max_length=64, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("профиль")
        verbose_name_plural = _("профили")

    def __str__(self) -> str:
        return f"Profile<{self.user_id}>"
