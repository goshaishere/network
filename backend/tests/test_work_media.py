import pytest
from django.test import Client

from tests.support import register_user


@pytest.mark.django_db
def test_work_dashboard_requires_auth():
    c = Client()
    r = c.get("/api/v1/work/dashboard/")
    assert r.status_code == 401

    reg = register_user(c, "work@example.com")
    r2 = c.get("/api/v1/work/dashboard/", HTTP_AUTHORIZATION=f"Bearer {reg['access']}")
    assert r2.status_code == 200
    assert "tasks_due" in r2.json()


@pytest.mark.django_db
def test_media_upload_requires_auth():
    c = Client()
    r = c.post("/api/v1/media/", {})
    assert r.status_code in (401, 403, 415)
