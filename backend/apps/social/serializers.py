from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import FriendRequest

User = get_user_model()


class UserMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "display_name")
        read_only_fields = fields


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user_detail = UserMiniSerializer(source="from_user", read_only=True)
    to_user_detail = UserMiniSerializer(source="to_user", read_only=True)

    class Meta:
        model = FriendRequest
        fields = (
            "id",
            "from_user",
            "to_user",
            "from_user_detail",
            "to_user_detail",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "status", "created_at")


class FriendRequestCreateSerializer(serializers.Serializer):
    to_user_id = serializers.IntegerField(min_value=1)
