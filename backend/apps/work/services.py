from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_work_event(board_id: int, payload: dict) -> None:
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        f"work_board_{board_id}",
        {"type": "work.event", "payload": payload},
    )
