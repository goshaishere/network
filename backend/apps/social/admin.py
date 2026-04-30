from django.contrib import admin

from .models import ContentReport


@admin.register(ContentReport)
class ContentReportAdmin(admin.ModelAdmin):
    list_display = ("id", "target_type", "target_id", "reporter", "created_at")
    list_filter = ("target_type",)
    ordering = ("-created_at",)
    raw_id_fields = ("reporter",)
