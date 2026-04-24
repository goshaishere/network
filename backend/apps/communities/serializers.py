from rest_framework import serializers

from .models import Community, CommunityPost


class CommunityListSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Community
        fields = ("id", "name", "slug", "description", "is_open", "members_count", "created_at")


class CommunityDetailSerializer(serializers.ModelSerializer):
    creator_id = serializers.IntegerField(source="creator.id", read_only=True)
    members_count = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()

    class Meta:
        model = Community
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "is_open",
            "creator_id",
            "created_at",
            "members_count",
            "is_member",
        )
        read_only_fields = ("id", "creator_id", "created_at", "members_count", "is_member")

    def get_members_count(self, obj: Community) -> int:
        return obj.memberships.count()

    def get_is_member(self, obj: Community) -> bool:
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.memberships.filter(user=request.user).exists()


class CommunityPostSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source="author.id", read_only=True)

    class Meta:
        model = CommunityPost
        fields = ("id", "author_id", "body", "created_at")
        read_only_fields = ("id", "author_id", "created_at")
