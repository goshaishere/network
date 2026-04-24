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
def test_work_group_board_and_task_crud_for_employee():
    c = Client()
    reg = register_user(c, "tasks-emp@example.com")
    User.objects.filter(pk=reg["user"]["id"]).update(is_employee=True, employment_kind="internal")
    auth = {"HTTP_AUTHORIZATION": f"Bearer {reg['access']}"}

    g = c.post(
        "/api/v1/tasks/groups/",
        data={"name": "Core Team", "slug": "core-team", "description": ""},
        content_type="application/json",
        **auth,
    )
    assert g.status_code == 201
    gid = g.json()["id"]

    b = c.post(
        "/api/v1/tasks/boards/",
        data={"group": gid, "name": "Delivery", "preset": "generic_pm"},
        content_type="application/json",
        **auth,
    )
    assert b.status_code == 201
    bid = b.json()["id"]

    columns = c.get("/api/v1/tasks/columns/", data={"board": bid}, **auth)
    assert columns.status_code == 200
    first_col = columns.json()[0]

    t = c.post(
        "/api/v1/tasks/",
        data={"board": bid, "column": first_col["id"], "title": "Ship MVP", "description": ""},
        content_type="application/json",
        **auth,
    )
    assert t.status_code == 201
    task_id = t.json()["id"]
    assert t.json()["title"] == "Ship MVP"

    move = c.patch(
        f"/api/v1/tasks/{task_id}/",
        data={"column": columns.json()[1]["id"]},
        content_type="application/json",
        **auth,
    )
    assert move.status_code == 200


@pytest.mark.django_db
def test_media_upload_requires_auth():
    c = Client()
    r = c.post("/api/v1/media/", {})
    assert r.status_code in (401, 403, 415)
