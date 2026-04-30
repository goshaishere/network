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
    assert data["redis"] == "n/a"
    assert "disk" in data
    assert "version" in data


def test_health_live():
    c = Client()
    r = c.get("/api/v1/health/live/")
    assert r.status_code == 200
    assert r.json()["status"] == "alive"


@pytest.mark.django_db
def test_health_ready():
    c = Client()
    r = c.get("/api/v1/health/ready/")
    assert r.status_code == 200
    assert r.json()["status"] == "ready"
