import pytest
from django.test import Client


@pytest.mark.django_db
def test_health_ok():
    c = Client()
    r = c.get("/api/v1/health/")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "ok"
    assert data["database"] == "up"
