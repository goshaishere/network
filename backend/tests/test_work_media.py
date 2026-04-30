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
def test_work_dashboard_employment_scope_partner_and_internal():
    c = Client()
    p = register_user(c, "scope-p@example.com")
    User.objects.filter(pk=p["user"]["id"]).update(is_employee=True, employment_kind="partner")
    rp = c.get("/api/v1/work/dashboard/", HTTP_AUTHORIZATION=f"Bearer {p['access']}")
    assert rp.status_code == 200
    assert rp.json().get("employment_scope") == "partner"
    assert "internal_extension_available" not in rp.json()

    i = register_user(c, "scope-i@example.com")
    User.objects.filter(pk=i["user"]["id"]).update(is_employee=True, employment_kind="internal")
    ri = c.get("/api/v1/work/dashboard/", HTTP_AUTHORIZATION=f"Bearer {i['access']}")
    assert ri.status_code == 200
    assert ri.json().get("employment_scope") == "internal"
    assert ri.json().get("internal_extension_available") is True


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
def test_board_preset_columns_match_roles_doc():
    """Пресеты колонок — ROLES-AND-TASKS §7.2."""
    c = Client()
    reg = register_user(c, "preset-doc@example.com")
    User.objects.filter(pk=reg["user"]["id"]).update(is_employee=True)
    auth = {"HTTP_AUTHORIZATION": f"Bearer {reg['access']}"}

    g = c.post(
        "/api/v1/tasks/groups/",
        data={"name": "Preset G", "slug": "preset-g", "description": ""},
        content_type="application/json",
        **auth,
    )
    gid = g.json()["id"]

    r_pm = c.post(
        "/api/v1/tasks/boards/",
        data={"group": gid, "name": "PM", "preset": "generic_pm"},
        content_type="application/json",
        **auth,
    )
    cols_pm = c.get(
        "/api/v1/tasks/columns/", data={"board": r_pm.json()["id"]}, **auth
    ).json()
    assert [x["semantic"] for x in cols_pm] == [
        "planned",
        "in_progress",
        "review",
        "paused",
        "done",
        "cancelled",
    ]

    r_sd = c.post(
        "/api/v1/tasks/boards/",
        data={"group": gid, "name": "SDLC", "preset": "it_sdlc"},
        content_type="application/json",
        **auth,
    )
    cols_sd = c.get(
        "/api/v1/tasks/columns/", data={"board": r_sd.json()["id"]}, **auth
    ).json()
    assert [x["semantic"] for x in cols_sd] == ["backlog", "development", "testing", "released"]

    r_c = c.post(
        "/api/v1/tasks/boards/",
        data={"group": gid, "name": "Emptyish", "preset": "custom"},
        content_type="application/json",
        **auth,
    )
    cols_c = c.get("/api/v1/tasks/columns/", data={"board": r_c.json()["id"]}, **auth).json()
    assert len(cols_c) == 1
    assert cols_c[0]["semantic"] == "planned"


@pytest.mark.django_db
def test_non_member_cannot_see_or_mutate_peer_group_tasks():
    c = Client()
    owner = register_user(c, "wg-owner@example.com")
    outsider = register_user(c, "wg-outsider@example.com")
    User.objects.filter(pk=owner["user"]["id"]).update(is_employee=True)
    User.objects.filter(pk=outsider["user"]["id"]).update(is_employee=True)
    auth_o = {"HTTP_AUTHORIZATION": f"Bearer {owner['access']}"}
    auth_x = {"HTTP_AUTHORIZATION": f"Bearer {outsider['access']}"}

    g = c.post(
        "/api/v1/tasks/groups/",
        data={"name": "Secret Pod", "slug": "secret-pod", "description": ""},
        content_type="application/json",
        **auth_o,
    )
    gid = g.json()["id"]
    b = c.post(
        "/api/v1/tasks/boards/",
        data={"group": gid, "name": "B1", "preset": "generic_pm"},
        content_type="application/json",
        **auth_o,
    )
    bid = b.json()["id"]
    cols = c.get("/api/v1/tasks/columns/", data={"board": bid}, **auth_o).json()
    t = c.post(
        "/api/v1/tasks/",
        data={"board": bid, "column": cols[0]["id"], "title": "X", "description": ""},
        content_type="application/json",
        **auth_o,
    )
    tid = t.json()["id"]

    assert c.get("/api/v1/tasks/columns/", data={"board": bid}, **auth_x).json() == []
    assert c.get("/api/v1/tasks/", data={"board": bid}, **auth_x).json() == []
    assert (
        c.patch(
            f"/api/v1/tasks/{tid}/",
            data={"title": "pwned"},
            content_type="application/json",
            **auth_x,
        ).status_code
        == 404
    )
    assert (
        c.post(
            "/api/v1/tasks/boards/",
            data={"group": gid, "name": "Intruder", "preset": "custom"},
            content_type="application/json",
            **auth_x,
        ).status_code
        == 403
    )


@pytest.mark.django_db
def test_media_upload_requires_auth():
    c = Client()
    r = c.post("/api/v1/media/", {})
    assert r.status_code in (401, 403, 415)
