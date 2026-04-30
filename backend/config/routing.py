"""WebSocket (Channels)."""

from apps.messaging.routing import websocket_urlpatterns as messaging_ws
from apps.work.routing import websocket_urlpatterns as work_ws

websocket_urlpatterns = [*messaging_ws, *work_ws]
