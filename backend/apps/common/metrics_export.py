"""Экспорт метрик Prometheus (один registry на процесс)."""

import time

from django.contrib.auth import get_user_model
from prometheus_client import CONTENT_TYPE_LATEST, CollectorRegistry, Gauge, generate_latest

from apps.common import health_checks as hc

_registry = CollectorRegistry()
_start = time.monotonic()

G_DB = Gauge(
    "network_db_up",
    "1 if PostgreSQL is reachable",
    registry=_registry,
)
G_REDIS = Gauge(
    "network_redis_up",
    "1 if Redis (Channels) is reachable when required, else 1",
    registry=_registry,
)
G_DISK_OK = Gauge(
    "network_disk_ok",
    "1 if free disk space is above critical threshold",
    registry=_registry,
)
G_USERS = Gauge(
    "network_users_total",
    "Number of user accounts",
    registry=_registry,
)
G_UPTIME = Gauge(
    "network_process_uptime_seconds",
    "Uptime of this worker process",
    registry=_registry,
)


def render_prometheus_metrics() -> tuple[bytes, str]:
    User = get_user_model()
    G_DB.set(1.0 if hc.check_database() else 0.0)
    rstate, _ = hc.check_redis()
    if rstate == "n/a":
        G_REDIS.set(1.0)
    elif rstate == "up":
        G_REDIS.set(1.0)
    else:
        G_REDIS.set(0.0)
    disk_state, _ = hc.check_disk()
    G_DISK_OK.set(1.0 if disk_state != "critical" else 0.0)
    try:
        G_USERS.set(User.objects.count())
    except Exception:
        G_USERS.set(0)
    G_UPTIME.set(time.monotonic() - _start)
    data = generate_latest(_registry)
    return data, CONTENT_TYPE_LATEST
