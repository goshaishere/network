import pytest
from django.test import Client

from tests.support import register_user


@pytest.mark.django_db
def test_metrics_requires_staff_or_token(settings):
    settings.METRICS_SCRAPE_TOKEN = "secret-metrics-token"
    c = Client()
    r = c.get("/api/v1/metrics/")
    assert r.status_code == 403

    ok = c.get("/api/v1/metrics/", HTTP_X_METRICS_TOKEN="secret-metrics-token")
    assert ok.status_code == 200
    assert b"network_db_up" in ok.content

    ok2 = c.get("/api/v1/metrics/?token=secret-metrics-token")
    assert ok2.status_code == 200


@pytest.mark.django_db
def test_metrics_staff_without_token(settings):
    settings.METRICS_SCRAPE_TOKEN = ""
    c = Client()
    reg = register_user(c, "metricsadmin@example.com", password="VerySecret1!")
    from django.contrib.auth import get_user_model

    User = get_user_model()
    User.objects.filter(pk=reg["user"]["id"]).update(is_staff=True, is_superuser=True)
    login = c.post(
        "/api/v1/auth/login/",
        data={"email": "metricsadmin@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {login.json()['access']}"}
    r = c.get("/api/v1/metrics/", **auth)
    assert r.status_code == 200
    assert b"network_users_total" in r.content
