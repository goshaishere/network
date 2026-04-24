"""Проверка hCaptcha (siteverify)."""

import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from django.conf import settings

logger = logging.getLogger(__name__)


def verify_hcaptcha_response(token: str | None) -> bool:
    """Возвращает True, если капча пройдена или проверка отключена (SKIP / нет секрета в dev)."""
    if getattr(settings, "HCAPTCHA_SKIP", False):
        return True
    secret = (getattr(settings, "HCAPTCHA_SECRET_KEY", None) or "").strip()
    if not secret:
        return True
    if not token or not str(token).strip():
        return False
    data = urllib.parse.urlencode(
        {"secret": secret, "response": str(token).strip()}
    ).encode()
    req = urllib.request.Request(
        "https://hcaptcha.com/siteverify",
        data=data,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = json.loads(resp.read().decode())
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        logger.warning("hCaptcha siteverify failed: %s", e)
        return False
    return bool(body.get("success"))
