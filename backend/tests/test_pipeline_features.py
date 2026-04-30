"""Тесты доработок пайплайна: группы прав, метрики, друзья, порядок колонок."""

import pytest
from django.contrib.auth import get_user_model

from tests.support import register_user

User = get_user_model()


@pytest.mark.django_db
def test_admin_permission_groups_and_catalog():
    c = pytest.importorskip("django.test").Client()
    admin_reg = register_user(c, "adm2@example.com", password="VerySecret1!")
    User.objects.filter(pk=admin_reg["user"]["id"]).update(is_staff=True, is_superuser=True)
    login = c.post(
        "/api/v1/auth/login/",
        data={"email": "adm2@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {login.json()['access']}"}

    cat = c.get("/api/v1/admin/permission-catalog/", **auth)
    assert cat.status_code == 200
    assert isinstance(cat.json(), list)
    assert any(x.get("slug") == "console.view_users" for x in cat.json())
    assert any(x.get("slug") == "console.moderate_communities" for x in cat.json())

    create = c.post(
        "/api/v1/admin/permission-groups/",
        data={
            "name": "Support",
            "slug": "support-team",
            "description": "",
            "permission_slugs": ["console.view_users", "console.view_audit"],
            "member_ids": [],
        },
        content_type="application/json",
        **auth,
    )
    assert create.status_code == 201, create.content
    gid = create.json()["id"]

    lst = c.get("/api/v1/admin/permission-groups/", **auth)
    assert lst.status_code == 200
    assert len(lst.json()) >= 1

    patch = c.patch(
        f"/api/v1/admin/permission-groups/{gid}/",
        data={"permission_slugs": ["console.view_users"]},
        content_type="application/json",
        **auth,
    )
    assert patch.status_code == 200


@pytest.mark.django_db
def test_effective_permissions_on_me_for_group_member():
    c = pytest.importorskip("django.test").Client()
    admin_reg = register_user(c, "adm3@example.com", password="VerySecret1!")
    User.objects.filter(pk=admin_reg["user"]["id"]).update(is_staff=True, is_superuser=True)
    u_reg = register_user(c, "member@example.com", password="VerySecret1!")
    uid = u_reg["user"]["id"]

    login = c.post(
        "/api/v1/auth/login/",
        data={"email": "adm3@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {login.json()['access']}"}

    c.post(
        "/api/v1/admin/permission-groups/",
        data={
            "name": "Readers",
            "slug": "readers",
            "permission_slugs": ["internal.tools"],
            "member_ids": [uid],
        },
        content_type="application/json",
        **auth,
    )

    ulogin = c.post(
        "/api/v1/auth/login/",
        data={"email": "member@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    uauth = {"HTTP_AUTHORIZATION": f"Bearer {ulogin.json()['access']}"}
    me = c.get("/api/v1/auth/me/", **uauth)
    assert me.status_code == 200
    assert "internal.tools" in me.json().get("effective_permission_slugs", [])


@pytest.mark.django_db
def test_metrics_endpoint_requires_staff():
    c = pytest.importorskip("django.test").Client()
    reg = register_user(c, "m1@example.com", password="VerySecret1!")
    login = c.post(
        "/api/v1/auth/login/",
        data={"email": "m1@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {login.json()['access']}"}
    r = c.get("/api/v1/metrics/", **auth)
    assert r.status_code == 403

    User.objects.filter(pk=reg["user"]["id"]).update(is_staff=True, is_superuser=True)
    login2 = c.post(
        "/api/v1/auth/login/",
        data={"email": "m1@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    auth2 = {"HTTP_AUTHORIZATION": f"Bearer {login2.json()['access']}"}
    r2 = c.get("/api/v1/metrics/", **auth2)
    assert r2.status_code == 200
    assert b"network_users_total" in r2.content


@pytest.mark.django_db
def test_friend_request_accept_flow():
    c = pytest.importorskip("django.test").Client()
    a = register_user(c, "fa@example.com", password="VerySecret1!")
    b = register_user(c, "fb@example.com", password="VerySecret1!")
    la = c.post(
        "/api/v1/auth/login/",
        data={"email": "fa@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    aa = {"HTTP_AUTHORIZATION": f"Bearer {la.json()['access']}"}
    create = c.post(
        "/api/v1/social/friend-requests/",
        data={"to_user_id": b["user"]["id"]},
        content_type="application/json",
        **aa,
    )
    assert create.status_code == 201
    fr_id = create.json()["id"]

    lb = c.post(
        "/api/v1/auth/login/",
        data={"email": "fb@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    ab = {"HTTP_AUTHORIZATION": f"Bearer {lb.json()['access']}"}
    acc = c.post(f"/api/v1/social/friend-requests/{fr_id}/accept/", **ab)
    assert acc.status_code == 200

    friends = c.get("/api/v1/social/friends/", **aa)
    assert friends.status_code == 200
    ids = [x["id"] for x in friends.json()]
    assert b["user"]["id"] in ids


@pytest.mark.django_db
def test_tasks_columns_reorder():
    c = pytest.importorskip("django.test").Client()
    reg = register_user(c, "wk@example.com", password="VerySecret1!")
    uid = reg["user"]["id"]
    User.objects.filter(pk=uid).update(is_employee=True, employment_kind="internal")
    login = c.post(
        "/api/v1/auth/login/",
        data={"email": "wk@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {login.json()['access']}"}

    g = c.post(
        "/api/v1/tasks/groups/",
        data={"name": "G1", "slug": "g1", "description": ""},
        content_type="application/json",
        **auth,
    )
    assert g.status_code == 201
    gid = g.json()["id"]
    b = c.post(
        "/api/v1/tasks/boards/",
        data={"group": gid, "name": "B1", "preset": "it_sdlc"},
        content_type="application/json",
        **auth,
    )
    bid = b.json()["id"]
    cols = c.get("/api/v1/tasks/columns/", {"board": bid}, **auth).json()
    order_before = [x["id"] for x in sorted(cols, key=lambda x: x["position"])]
    rev = list(reversed(order_before))
    r = c.post(
        "/api/v1/tasks/columns/reorder/",
        data={"board": bid, "order": rev},
        content_type="application/json",
        **auth,
    )
    assert r.status_code == 200
    out = r.json()
    assert [x["id"] for x in out] == rev


@pytest.mark.django_db
def test_admin_organization_and_department():
    c = pytest.importorskip("django.test").Client()
    admin_reg = register_user(c, "orgadm@example.com", password="VerySecret1!")
    User.objects.filter(pk=admin_reg["user"]["id"]).update(is_staff=True, is_superuser=True)
    login = c.post(
        "/api/v1/auth/login/",
        data={"email": "orgadm@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {login.json()['access']}"}
    org = c.post(
        "/api/v1/admin/organizations/",
        data={"name": "Acme"},
        content_type="application/json",
        **auth,
    )
    assert org.status_code == 201
    oid = org.json()["id"]
    dep = c.post(
        "/api/v1/admin/departments/",
        data={"organization": oid, "name": "IT", "parent": None},
        content_type="application/json",
        **auth,
    )
    assert dep.status_code == 201
    did = dep.json()["id"]

    target = register_user(c, "deptuser@example.com", password="VerySecret1!")
    patch = c.patch(
        "/api/v1/admin/users/",
        data={"id": target["user"]["id"], "department": did},
        content_type="application/json",
        **auth,
    )
    assert patch.status_code == 200
    assert patch.json()["department"] == did
