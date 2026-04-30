from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from apps.console.permissions_catalog import ALL_PERMISSION_SLUGS


class Organization(models.Model):
    name = models.CharField("название", max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "компания"
        verbose_name_plural = "компании"

    def __str__(self) -> str:
        return self.name


class Department(models.Model):
    organization = models.ForeignKey(
        Organization, on_delete=models.CASCADE, related_name="departments"
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    name = models.CharField("название", max_length=200)

    class Meta:
        ordering = ("organization_id", "name")
        verbose_name = "отдел"
        verbose_name_plural = "отделы"

    def __str__(self) -> str:
        return f"{self.organization.name} / {self.name}"


class UserPermissionGroup(models.Model):
    """Именованные группы учётных записей для выдачи разрешений (не WorkGroup)."""

    name = models.CharField("название", max_length=160)
    slug = models.SlugField("slug", max_length=80, unique=True, db_index=True)
    description = models.TextField("описание", blank=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="permission_groups",
        blank=True,
    )
    permission_slugs = models.JSONField(
        default=list,
        blank=True,
        help_text="Список кодов из каталога разрешений консоли.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "группа пользователей (права)"
        verbose_name_plural = "группы пользователей (права)"

    def __str__(self) -> str:
        return self.name

    def clean(self) -> None:
        super().clean()
        bad = [s for s in (self.permission_slugs or []) if s not in ALL_PERMISSION_SLUGS]
        if bad:
            raise ValidationError({"permission_slugs": [f"Неизвестные коды: {bad}"]})


class AdminAuditLog(models.Model):
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="admin_actions"
    )
    action = models.CharField(max_length=120)
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="admin_audit_targets",
    )
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-id",)
