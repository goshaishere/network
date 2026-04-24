import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from tests.support import register_user

User = get_user_model()


@pytest.mark.django_db
def test_work_dashboard_requires_login():
    c = Client()
    r = c.get("/api/v1/work/dashboard/")
    assert r.status_code in (401, 403)


@pytest.mark.django_db
def test_work_dashboard_forbidden_plain_user():
    c = Client()
    reg = register_user(c, "plain-work@example.com")
    r = c.get("/api/v1/work/dashboard/", HTTP_AUTHORIZATION=f"Bearer {reg['access']}")
    assert r.status_code == 403


@pytest.mark.django_db
def test_work_dashboard_ok_for_employee_or_staff():
    c = Client()
    reg = register_user(c, "emp-work@example.com")
    User.objects.filter(pk=reg["user"]["id"]).update(is_employee=True)
    r = c.get("/api/v1/work/dashboard/", HTTP_AUTHORIZATION=f"Bearer {reg['access']}")
    assert r.status_code == 200
    body = r.json()
    assert "tasks_due" in body
    assert "note" in body


@pytest.mark.django_db
def test_tasks_stubs_require_employee():
    c = Client()
    reg = register_user(c, "tasks-plain@example.com")
    auth = {"HTTP_AUTHORIZATION": f"Bearer {reg['access']}"}
    assert c.get("/api/v1/tasks/groups/", **auth).status_code == 403
    assert c.get("/api/v1/tasks/boards/", **auth).status_code == 403
    User.objects.filter(pk=reg["user"]["id"]).update(is_employee=True)
    assert c.get("/api/v1/tasks/groups/", **auth).status_code == 200
    assert c.get("/api/v1/tasks/boards/", **auth).status_code == 200


@pytest.mark.django_db
def test_media_upload_requires_auth():
    c = Client()
    r = c.post("/api/v1/media/", {})
    assert r.status_code in (401, 403, 415)
