"""Production: DEBUG выключен, секреты только из окружения."""

import os

from .base import *  # noqa: F403, F405

DEBUG = False
SECRET_KEY = os.environ["SECRET_KEY"]

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/2",
    }
}
