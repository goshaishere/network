from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.communities.models import CommunityPost
from apps.walls.models import WallPost

from .models import ContentReport, FriendRequest

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


class ContentReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentReport
        fields = ("id", "target_type", "target_id", "reason", "created_at")
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        tt = attrs["target_type"]
        tid = attrs["target_id"]
        if tt == ContentReport.TargetType.WALL_POST:
            if not WallPost.objects.filter(pk=tid).exists():
                raise serializers.ValidationError({"target_id": ["Пост не найден."]})
        elif tt == ContentReport.TargetType.COMMUNITY_POST:
            if not CommunityPost.objects.filter(pk=tid).exists():
                raise serializers.ValidationError({"target_id": ["Пост не найден."]})
        return attrs

    def create(self, validated_data):
        validated_data["reporter"] = self.context["request"].user
        return super().create(validated_data)
