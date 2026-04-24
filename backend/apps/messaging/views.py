from django.contrib.auth import get_user_model
from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response

from apps.common.pagination import IdCursorPagination

from .models import Conversation, Message
from .serializers import (
    ConversationCreateSerializer,
    ConversationListSerializer,
    MessageSerializer,
)
from .services import broadcast_new_message

User = get_user_model()


def _find_direct(u1, u2):
    return (
        Conversation.objects.annotate(pc=Count("participants"))
        .filter(kind=Conversation.Kind.DIRECT, pc=2, participants=u1)
        .filter(participants=u2)
        .first()
    )


class ConversationListCreateView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ConversationListSerializer

    def get_queryset(self):
        return (
            Conversation.objects.filter(participants=self.request.user)
            .prefetch_related("participants")
            .order_by("-created_at")
        )

    def post(self, request, *args, **kwargs):
        ser = ConversationCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        other_id = ser.validated_data["participant_id"]
        if other_id == request.user.id:
            raise ValidationError({"participant_id": ["Нельзя создать диалог с собой."]})
        other = get_object_or_404(User, pk=other_id)
        existing = _find_direct(request.user, other)
        if existing:
            return Response(
                ConversationListSerializer(existing, context={"request": request}).data,
                status=status.HTTP_200_OK,
            )
        c = Conversation.objects.create(kind=Conversation.Kind.DIRECT)
        c.participants.add(request.user, other)
        return Response(
            ConversationListSerializer(c, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )


class MessageListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = MessageSerializer
    pagination_class = IdCursorPagination

    def get_queryset(self):
        cid = self.kwargs["pk"]
        conv = get_object_or_404(Conversation, pk=cid)
        if not conv.participants.filter(pk=self.request.user.id).exists():
            raise PermissionDenied()
        qs = Message.objects.filter(conversation_id=cid).select_related("sender")
        before = self.request.query_params.get("before")
        if before and before.isdigit():
            qs = qs.filter(id__lt=int(before))
        return qs

    def perform_create(self, serializer):
        cid = self.kwargs["pk"]
        conv = get_object_or_404(Conversation, pk=cid)
        if not conv.participants.filter(pk=self.request.user.id).exists():
            raise PermissionDenied()
        msg = serializer.save(conversation=conv, sender=self.request.user)
        broadcast_new_message(conv.id, MessageSerializer(msg).data)
