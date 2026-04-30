from django.urls import re_path

from .consumers import WorkBoardConsumer

websocket_urlpatterns = [
    re_path(r"^ws/work/?$", WorkBoardConsumer.as_asgi()),
]
