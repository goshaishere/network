from django.contrib import admin

from .models import Community, CommunityMembership, CommunityPost


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "is_open", "creator", "created_at")


@admin.register(CommunityMembership)
class CommunityMembershipAdmin(admin.ModelAdmin):
    list_display = ("community", "user", "role", "joined_at")


@admin.register(CommunityPost)
class CommunityPostAdmin(admin.ModelAdmin):
    list_display = ("community", "author", "created_at")
