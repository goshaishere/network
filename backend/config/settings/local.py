"""Локальная разработка (DEBUG=True по умолчанию)."""

import os

from .base import *  # noqa: F403, F405

DEBUG = os.environ.get("DEBUG", "true").lower() in ("1", "true", "yes")  # noqa: F405

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.environ.get("EMAIL_HOST", "localhost")  # noqa: F405
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "1025"))
EMAIL_USE_TLS = os.environ.get("EMAIL_USE_TLS", "false").lower() in ("1", "true")
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "network@localhost")

# Быстрые тесты без Postgres: USE_SQLITE=1 python manage.py migrate
if os.environ.get("USE_SQLITE") == "1":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
