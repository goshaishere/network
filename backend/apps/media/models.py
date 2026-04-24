from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class UploadedFile(models.Model):
    file = models.FileField(_("файл"), upload_to="uploads/%Y/%m/")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploads",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-id",)
