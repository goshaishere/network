"""Production: DEBUG выключен, секреты только из окружения."""

import os

from .base import *  # noqa: F403, F405

DEBUG = False
SECRET_KEY = os.environ["SECRET_KEY"]
