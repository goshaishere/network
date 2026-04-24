"""Настройки для pytest: in-memory channel layer (без Redis для WS broadcast)."""

from .local import *  # noqa: F403, F405

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}
