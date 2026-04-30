from rest_framework import serializers

from apps.media.models import UploadedFile

from .models import WallPost


class WallPostSerializer(serializers.ModelSerializer):
    author_id = serializers.IntegerField(source="author.id", read_only=True)
    author_display_name = serializers.CharField(source="author.display_name", read_only=True)
    wall_owner_id = serializers.IntegerField(source="wall_owner.id", read_only=True)
    attachment_url = serializers.SerializerMethodField()
    uploaded_file_id = serializers.PrimaryKeyRelatedField(
        queryset=UploadedFile.objects.all(),
        source="uploaded_file",
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = WallPost
        fields = (
            "id",
            "wall_owner_id",
            "author_id",
            "author_display_name",
            "body",
            "uploaded_file_id",
            "attachment_url",
            "hidden_from_feed",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "author_id",
            "author_display_name",
            "wall_owner_id",
            "attachment_url",
            "created_at",
            "updated_at",
        )

    def get_attachment_url(self, obj: WallPost) -> str:
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
