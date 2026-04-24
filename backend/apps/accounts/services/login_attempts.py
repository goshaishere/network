"""Счётчик неудачных попыток входа (кэш Django)."""

from django.core.cache import cache

FAIL_WINDOW_SEC = 900  # 15 минут

FAIL_KEY = "login_fail:v1:{ip}:{email}"


def client_ip(request) -> str:
    if not request:
        return ""
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "") or ""


def fail_key(request, email: str) -> str:
    return FAIL_KEY.format(ip=client_ip(request), email=email.strip().lower())


def get_fail_count(key: str) -> int:
    return int(cache.get(key) or 0)


def increment_fail(key: str) -> None:
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1, FAIL_WINDOW_SEC)


def clear_fail(key: str) -> None:
    cache.delete(key)
