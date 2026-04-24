"""WebSocket (Channels)."""

from apps.messaging.routing import websocket_urlpatterns as messaging_ws

websocket_urlpatterns = list(messaging_ws)
