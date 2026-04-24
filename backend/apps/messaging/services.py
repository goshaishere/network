import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

logger = logging.getLogger(__name__)


def broadcast_new_message(conversation_id: int, payload: dict) -> None:
    """Публикация в группу WS; при сбое канала сообщение в БД уже сохранено — не падаем."""
    layer = get_channel_layer()
    if layer is None:
        return
    try:
        async_to_sync(layer.group_send)(
            f"conversation_{conversation_id}",
            {"type": "chat.message", "payload": payload},
        )
    except Exception as e:
        logger.warning("messaging broadcast failed conv=%s: %s", conversation_id, e)
