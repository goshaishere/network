from rest_framework import serializers

from apps.media.models import UploadedFile

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
    attachment_url = serializers.SerializerMethodField()
    uploaded_file_id = serializers.PrimaryKeyRelatedField(
        queryset=UploadedFile.objects.all(),
        source="uploaded_file",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = CommunityPost
        fields = (
            "id",
            "author_id",
            "body",
            "uploaded_file_id",
            "attachment_url",
            "hidden_from_feed",
            "created_at",
        )
        read_only_fields = ("id", "author_id", "attachment_url", "created_at")

    def get_attachment_url(self, obj: CommunityPost) -> str:
        uf = getattr(obj, "uploaded_file", None)
        if not uf or not uf.file:
            return ""
        request = self.context.get("request")
        url = uf.file.url
        if request:
            return request.build_absolute_uri(url)
        return url

    def validate_uploaded_file_id(self, value: UploadedFile | None):
        if value is None:
            return value
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            raise serializers.ValidationError("Нужна авторизация.")
        if value.uploaded_by_id != request.user.id:
            raise serializers.ValidationError("Можно прикреплять только свои загрузки.")
        return value

    def validate(self, attrs):
        if self.instance is None:
            attrs.pop("hidden_from_feed", None)
        return attrs
