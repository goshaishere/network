from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Community(models.Model):
    name = models.CharField(_("название"), max_length=200)
    slug = models.SlugField(_("slug"), max_length=80, unique=True, db_index=True)
    description = models.TextField(_("описание"), blank=True)
    is_open = models.BooleanField(_("открытое вступление"), default=True)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="communities_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("сообщество")
        verbose_name_plural = _("сообщества")

    def __str__(self) -> str:
        return self.slug


class CommunityMembership(models.Model):
    class Role(models.TextChoices):
        MEMBER = "member", _("Участник")
        MODERATOR = "moderator", _("Модератор")

    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="memberships")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="community_memberships",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("community", "user")


class CommunityPost(models.Model):
    community = models.ForeignKey(Community, on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    body = models.TextField(_("текст"))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
