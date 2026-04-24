from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_new_message(conversation_id: int, payload: dict) -> None:
    layer = get_channel_layer()
    if layer is None:
        return
    async_to_sync(layer.group_send)(
        f"conversation_{conversation_id}",
        {"type": "chat.message", "payload": payload},
    )
