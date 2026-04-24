from unittest.mock import patch

import pytest
from django.contrib.auth import get_user_model
from django.test import Client, override_settings

User = get_user_model()


@pytest.mark.django_db
def test_register_login_me_logout():
    c = Client()
    r = c.post(
        "/api/v1/auth/register/",
        data={
            "email": "u1@example.com",
            "display_name": "User One",
            "password": "verySecret1!",
            "password_confirm": "verySecret1!",
        },
        content_type="application/json",
    )
    assert r.status_code == 201
    body = r.json()
    assert body["user"]["email"] == "u1@example.com"
    assert "access" in body and "refresh" in body

    access = body["access"]
    r2 = c.get("/api/v1/auth/me/", HTTP_AUTHORIZATION=f"Bearer {access}")
    assert r2.status_code == 200
    assert r2.json()["email"] == "u1@example.com"

    r3 = c.post(
        "/api/v1/auth/login/",
        data={"email": "u1@example.com", "password": "verySecret1!"},
        content_type="application/json",
    )
    assert r3.status_code == 200
    refresh = r3.json()["refresh"]

    r4 = c.post("/api/v1/auth/logout/", data={"refresh": refresh}, content_type="application/json")
    assert r4.status_code == 200


@pytest.mark.django_db
def test_password_reset_confirm_invalid():
    c = Client()
    r = c.post(
        "/api/v1/auth/password/reset/confirm/",
        data={
            "uid": "bad",
            "token": "bad",
            "new_password": "newSecret12!",
            "new_password_confirm": "newSecret12!",
        },
        content_type="application/json",
    )
    assert r.status_code == 400


@pytest.mark.django_db
@override_settings(
    LOGIN_CAPTCHA_THRESHOLD=3,
    HCAPTCHA_SKIP=False,
    HCAPTCHA_SECRET_KEY="test-secret",
)
@patch("apps.accounts.serializers.verify_hcaptcha_response")
def test_login_requires_captcha_after_failed_attempts(mock_verify):
    """После N неверных паролей без captcha_token — ошибка captcha_required."""
    mock_verify.side_effect = lambda t: bool(t and str(t).strip())

    c = Client()
    email = "cap@example.com"
    pwd = "verySecret1!"
    reg = c.post(
        "/api/v1/auth/register/",
        data={
            "email": email,
            "display_name": "Cap User",
            "password": pwd,
            "password_confirm": pwd,
        },
        content_type="application/json",
    )
    assert reg.status_code == 201

    bad = {"email": email, "password": "wrong"}
    for _ in range(3):
        r = c.post("/api/v1/auth/login/", data=bad, content_type="application/json")
        assert r.status_code == 401

    r4 = c.post("/api/v1/auth/login/", data=bad, content_type="application/json")
    assert r4.status_code == 400
    body = r4.json()
    assert body.get("code") == "captcha_required"

    r5 = c.post(
        "/api/v1/auth/login/",
        data={**bad, "captcha_token": "tok"},
        content_type="application/json",
    )
    assert r5.status_code == 401

    r_ok = c.post(
        "/api/v1/auth/login/",
        data={"email": email, "password": pwd, "captcha_token": "tok"},
        content_type="application/json",
    )
    assert r_ok.status_code == 200
    assert "access" in r_ok.json()
