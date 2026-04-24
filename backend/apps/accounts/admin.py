from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    ordering = ("email",)
    list_display = (
        "email",
        "display_name",
        "is_staff",
        "is_employee",
        "employment_kind",
        "is_active",
        "date_joined",
    )
    search_fields = ("email", "display_name", "first_name", "last_name")
    readonly_fields = ("date_joined", "last_login")

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (_("Персональные данные"), {"fields": ("display_name", "first_name", "last_name")}),
        (
            _("Права"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_employee",
                    "employment_kind",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Даты"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "display_name",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
