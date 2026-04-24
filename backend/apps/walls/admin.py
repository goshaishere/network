from django.contrib import admin

from .models import WallPost


@admin.register(WallPost)
class WallPostAdmin(admin.ModelAdmin):
    list_display = ("id", "wall_owner", "author", "created_at")
    search_fields = ("body",)
