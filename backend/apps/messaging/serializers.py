from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Conversation, Message

User = get_user_model()


class ConversationListSerializer(serializers.ModelSerializer):
    other_user_id = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ("id", "kind", "other_user_id", "created_at")

    def get_other_user_id(self, obj: Conversation):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        for uid in obj.participants.values_list("id", flat=True):
            if uid != request.user.id:
                return uid
        return None


class ConversationCreateSerializer(serializers.Serializer):
    participant_id = serializers.IntegerField()

    def validate_participant_id(self, value: int) -> int:
        if not User.objects.filter(pk=value).exists():
            raise serializers.ValidationError("Пользователь не найден.")
        return value


class MessageSerializer(serializers.ModelSerializer):
    sender_id = serializers.IntegerField(source="sender.id", read_only=True)

    class Meta:
        model = Message
        fields = ("id", "sender_id", "body", "created_at")
        read_only_fields = ("id", "sender_id", "created_at")
