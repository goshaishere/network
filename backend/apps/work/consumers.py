from urllib.parse import parse_qs

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken


class WorkBoardConsumer(AsyncJsonWebsocketConsumer):
    user_id: int | None = None

    async def connect(self):
        self.user_id = self._authenticate_user_id()
        if self.user_id is None:
            await self.close(code=4401)
            return
        await self.accept()

    async def disconnect(self, code):
        if getattr(self, "group_board", None):
            await self.channel_layer.group_discard(self.group_board, self.channel_name)

    async def receive_json(self, content, **kwargs):
        if content.get("type") != "subscribe":
            return
        board_id = content.get("board")
        if not isinstance(board_id, int):
            await self.send_json({"error": "invalid_board"})
            return
        if getattr(self, "group_board", None):
            await self.channel_layer.group_discard(self.group_board, self.channel_name)
        self.group_board = f"work_board_{board_id}"
        await self.channel_layer.group_add(self.group_board, self.channel_name)
        await self.send_json({"detail": "subscribed", "board": board_id})

    async def work_event(self, event):
        await self.send_json(event["payload"])

    def _authenticate_user_id(self) -> int | None:
        qs = parse_qs(self.scope.get("query_string", b"").decode())
        raw = (qs.get("token") or [None])[0]
        if not raw:
            return None
        try:
            token = AccessToken(raw)
            return int(token["user_id"])
        except (TokenError, InvalidToken, KeyError, ValueError, TypeError):
            return None
