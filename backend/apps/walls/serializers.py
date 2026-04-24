from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import WallPost

User = get_user_model()


class WallPostSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    author_display_name = serializers.CharField(source="author.display_name", read_only=True)
    wall_owner_id = serializers.IntegerField(source="wall_owner.id", read_only=True)

    class Meta:
        model = WallPost
        fields = (
            "id",
            "wall_owner_id",
            "author_id",
            "author_display_name",
            "body",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "author_id",
            "author_display_name",
            "wall_owner_id",
            "created_at",
            "updated_at",
        )
