from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.communities.models import Community, CommunityPost
from apps.console.permissions_catalog import ALL_PERMISSION_SLUGS
from apps.console.services.permissions import get_effective_permission_slugs

from .models import AdminAuditLog, Department, Organization, UserPermissionGroup

User = get_user_model()


class AdminUserSerializer(serializers.ModelSerializer):
    permission_groups = serializers.SerializerMethodField(read_only=True)
    effective_permission_slugs = serializers.SerializerMethodField(read_only=True)
    permission_group_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        write_only=True,
        required=False,
    )

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
            "department",
            "permission_groups",
            "effective_permission_slugs",
            "permission_group_ids",
        )
        read_only_fields = ("id", "email")

    def get_permission_groups(self, obj):
        return [
            {"id": g.id, "name": g.name, "slug": g.slug}
            for g in obj.permission_groups.all().order_by("name")
        ]

    def get_effective_permission_slugs(self, obj):
        return sorted(get_effective_permission_slugs(obj))

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["permission_group_ids"] = list(instance.permission_groups.values_list("id", flat=True))
        return data

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

    def update(self, instance, validated_data):
        group_ids = validated_data.pop("permission_group_ids", None)
        user = super().update(instance, validated_data)
        if group_ids is not None:
            groups = UserPermissionGroup.objects.filter(pk__in=group_ids)
            user.permission_groups.set(groups)
        return user


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


class UserPermissionGroupSerializer(serializers.ModelSerializer):
    member_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        required=False,
    )

    class Meta:
        model = UserPermissionGroup
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "permission_slugs",
            "member_ids",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["member_ids"] = list(instance.members.values_list("id", flat=True))
        return data

    def validate_permission_slugs(self, value):
        if not isinstance(value, list):
            raise serializers.ValidationError("Ожидается список строк.")
        bad = [s for s in value if s not in ALL_PERMISSION_SLUGS]
        if bad:
            raise serializers.ValidationError(f"Неизвестные коды: {bad}")
        return value

    def validate_slug(self, value: str) -> str:
        return value.strip().lower()

    def create(self, validated_data):
        member_ids = validated_data.pop("member_ids", [])
        group = UserPermissionGroup(**validated_data)
        group.full_clean()
        group.save()
        if member_ids:
            group.members.set(User.objects.filter(pk__in=member_ids))
        return group

    def update(self, instance, validated_data):
        member_ids = validated_data.pop("member_ids", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        instance.full_clean()
        instance.save()
        if member_ids is not None:
            instance.members.set(User.objects.filter(pk__in=member_ids))
        return instance


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name", "created_at")
        read_only_fields = ("id", "created_at")


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ("id", "organization", "parent", "name")
        read_only_fields = ("id",)


class AdminCommunitySerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Community
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "is_open",
            "created_at",
            "members_count",
            "posts_count",
        )
        read_only_fields = ("id", "slug", "created_at", "members_count", "posts_count")


class AdminCommunityPostSerializer(serializers.ModelSerializer):
    author_email = serializers.EmailField(source="author.email", read_only=True)

    class Meta:
        model = CommunityPost
        fields = ("id", "community", "author", "author_email", "body", "created_at")
        read_only_fields = ("id", "community", "author", "author_email", "body", "created_at")
