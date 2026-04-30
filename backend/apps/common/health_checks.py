"""Проверки для health/ready и экспорта метрик."""

import os
import shutil
from typing import Literal

from django.conf import settings

RedisState = Literal["up", "down", "n/a"]
DiskState = Literal["ok", "low", "critical"]


def check_database() -> bool:
    from django.db import connection

    try:
        connection.ensure_connection()
        return True
    except Exception:
        return False


def channel_layer_uses_redis() -> bool:
    backend = settings.CHANNEL_LAYERS.get("default", {}).get("BACKEND", "")
    return "redis" in backend.lower()


def check_redis() -> tuple[RedisState, str]:
    if not channel_layer_uses_redis():
        return "n/a", "InMemory или не Redis — проверка не требуется."
    try:
        import redis

        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=int(settings.REDIS_PORT),
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        if client.ping():
            return "up", "PONG"
        return "down", "ping false"
    except Exception as exc:
        return "down", str(exc)[:200]


def check_disk() -> tuple[DiskState, int]:
    """
    Возвращает (состояние, свободно байт на том же разделе, что и MEDIA_ROOT / BASE_DIR).
    """
    path = getattr(settings, "MEDIA_ROOT", None) or settings.BASE_DIR
    try:
        usage = shutil.disk_usage(path)
        free_mb = usage.free // (1024 * 1024)
        min_mb = int(os.environ.get("DISK_FREE_MIN_MB", "100"))
        critical_mb = max(50, min_mb // 2)
        if free_mb < critical_mb:
            return "critical", usage.free
        if free_mb < min_mb:
            return "low", usage.free
        return "ok", usage.free
    except Exception:
        return "ok", -1


def overall_health_status() -> dict:
    """Сводка для GET /api/v1/health/."""
    db_ok = check_database()
    redis_state, redis_detail = check_redis()
    disk_state, free_bytes = check_disk()

    payload = {
        "status": "ok",
        "database": "up" if db_ok else "down",
        "redis": redis_state,
        "redis_detail": redis_detail if redis_state != "n/a" else None,
        "disk": disk_state,
        "disk_free_bytes": free_bytes if free_bytes >= 0 else None,
        "version": os.environ.get("APP_VERSION", "").strip() or "unknown",
    }

    http_status = 200
    if not db_ok:
        payload["status"] = "degraded"
        http_status = 503
    elif redis_state == "down":
        payload["status"] = "degraded"
        http_status = 503
    elif disk_state == "critical":
        payload["status"] = "degraded"
        http_status = 503
    elif disk_state == "low":
        payload["status"] = "degraded"

    return payload, http_status


def is_ready() -> bool:
    if not check_database():
        return False
    r, _ = check_redis()
    if r == "down":
        return False
    disk_state, _ = check_disk()
    if disk_state == "critical":
        return False
    return True
