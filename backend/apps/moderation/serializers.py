from rest_framework import serializers

from apps.social.models import ContentReport


class ModerationReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentReport
        fields = (
            "id",
            "reporter",
            "target_type",
            "target_id",
            "reason",
            "status",
            "assigned_to",
            "decision",
            "resolution_note",
            "resolved_at",
            "resolved_by",
            "created_at",
        )
        read_only_fields = ("id", "reporter", "created_at", "resolved_at", "resolved_by")
