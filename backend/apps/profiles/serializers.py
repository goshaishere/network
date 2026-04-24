from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Profile

User = get_user_model()


class ProfileMeSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    display_name = serializers.CharField(source="user.display_name", read_only=True)

    class Meta:
        model = Profile
        fields = (
            "email",
            "display_name",
            "bio",
            "avatar",
            "locale",
            "privacy",
            "default_landing",
            "updated_at",
        )
        read_only_fields = ("email", "display_name", "updated_at")


class ProfileMeWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ("bio", "avatar", "locale", "privacy", "default_landing")


class ProfilePublicSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(source="user.display_name", read_only=True)

    class Meta:
        model = Profile
        fields = ("display_name", "bio", "avatar", "locale", "privacy")


class DashboardLayoutSerializer(serializers.Serializer):
    layout = serializers.JSONField()

    def validate_layout(self, value):
        if not isinstance(value, dict):
            raise serializers.ValidationError("Ожидается объект JSON.")
        return value
