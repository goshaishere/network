from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Пользователь с входом по email (без username)."""

    username = None
    email = models.EmailField(_("email"), unique=True, db_index=True)
    display_name = models.CharField(_("отображаемое имя"), max_length=150, blank=True)
    is_employee = models.BooleanField(
        _("сотрудник (рабочий контур)"),
        default=False,
        help_text=_("Доступ к /work и задачам; выставляет администратор."),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        verbose_name = _("пользователь")
        verbose_name_plural = _("пользователи")

    def __str__(self) -> str:
        return self.email
