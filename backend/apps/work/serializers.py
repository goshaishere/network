from rest_framework import serializers

from .models import WorkBoard, WorkColumn, WorkGroup, WorkTask


class WorkGroupSerializer(serializers.ModelSerializer):
    members_count = serializers.IntegerField(read_only=True)
    my_role = serializers.SerializerMethodField()

    class Meta:
        model = WorkGroup
        fields = (
            "id",
            "name",
            "slug",
            "description",
            "created_by",
            "created_at",
            "members_count",
            "my_role",
        )
        read_only_fields = ("created_by", "created_at", "members_count", "my_role")

    def get_my_role(self, obj):
        user = self.context["request"].user
        m = obj.memberships.filter(user=user).first()
        return m.role if m else None


class WorkBoardSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkBoard
        fields = ("id", "group", "name", "preset", "created_at")
        read_only_fields = ("created_at",)


class WorkColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkColumn
        fields = ("id", "board", "title", "semantic", "position")


class WorkTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkTask
        fields = (
            "id",
            "board",
            "column",
            "title",
            "description",
            "assignee",
            "created_by",
            "due_date",
            "position",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("created_by", "created_at", "updated_at")

    def validate(self, attrs):
        board = attrs.get("board") or getattr(self.instance, "board", None)
        column = attrs.get("column") or getattr(self.instance, "column", None)
        if board and column and column.board_id != board.id:
            raise serializers.ValidationError({"column": ["Колонка не принадлежит этой доске."]})
        return attrs
