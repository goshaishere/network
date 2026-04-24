from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import AdminAuditLog

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "display_name",
            "is_staff",
            "is_employee",
            "employment_kind",
            "is_active",
        )
        read_only_fields = ("id", "email")

    def validate(self, attrs):
        is_employee = attrs.get("is_employee", getattr(self.instance, "is_employee", False))
        employment_kind = attrs.get(
            "employment_kind",
            getattr(self.instance, "employment_kind", ""),
        )
        if is_employee and not employment_kind:
            raise serializers.ValidationError(
                {"employment_kind": ["Укажите тип занятости для сотрудника (internal/partner)."]}
            )
        if not is_employee and employment_kind:
            raise serializers.ValidationError(
                {"employment_kind": ["У обычного пользователя поле должно быть пустым."]}
            )
        return attrs


class AdminAuditLogSerializer(serializers.ModelSerializer):
    actor_email = serializers.EmailField(source="actor.email", read_only=True)
    target_email = serializers.EmailField(source="target_user.email", read_only=True)

    class Meta:
        model = AdminAuditLog
        fields = (
            "id",
            "actor",
            "actor_email",
            "action",
            "target_user",
            "target_email",
            "payload",
            "created_at",
        )
