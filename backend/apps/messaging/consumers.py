from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken


@database_sync_to_async
def user_in_conversation(user_id: int, conversation_id: int) -> bool:
    from .models import Conversation

    return Conversation.objects.filter(
        pk=conversation_id,
        participants__id=user_id,
    ).exists()


class MessagingConsumer(AsyncJsonWebsocketConsumer):
    user_id: int | None = None

    async def connect(self):
        self.user_id = await self._authenticate()
        if self.user_id is None:
            await self.close(code=4401)
            return
        self.group_user = f"user_{self.user_id}"
        await self.channel_layer.group_add(self.group_user, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        if getattr(self, "group_user", None):
            await self.channel_layer.group_discard(self.group_user, self.channel_name)
        if getattr(self, "group_conv", None):
            await self.channel_layer.group_discard(self.group_conv, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("type") == "subscribe" and "conversation" in content:
            cid = int(content["conversation"])
            ok = await user_in_conversation(self.user_id, cid)
            if not ok:
                await self.send_json({"error": "forbidden"})
                return
            if getattr(self, "group_conv", None):
                await self.channel_layer.group_discard(self.group_conv, self.channel_name)
            self.group_conv = f"conversation_{cid}"
            await self.channel_layer.group_add(self.group_conv, self.channel_name)
            await self.send_json({"detail": "subscribed", "conversation": cid})

    async def chat_message(self, event):
        await self.send_json(event["payload"])

    async def _authenticate(self) -> int | None:
        qs = parse_qs(self.scope.get("query_string", b"").decode())
        raw = (qs.get("token") or [None])[0]
        if not raw:
            return None
        try:
            token = AccessToken(raw)
            return int(token["user_id"])
        except (TokenError, InvalidToken, KeyError, ValueError, TypeError):
            return None
