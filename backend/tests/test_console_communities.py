"""Модерация сообществ из админ-консоли (фаза 9)."""

import pytest
from django.contrib.auth import get_user_model

from tests.support import register_user

User = get_user_model()


@pytest.mark.django_db
def test_admin_communities_list_patch_and_delete_post():
    c = pytest.importorskip("django.test").Client()
    admin_reg = register_user(c, "adm-com@example.com", password="VerySecret1!")
    User.objects.filter(pk=admin_reg["user"]["id"]).update(is_staff=True, is_superuser=True)
    user_reg = register_user(c, "com-author@example.com", password="VerySecret1!")

    ulogin = c.post(
        "/api/v1/auth/login/",
        data={"email": "com-author@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    uauth = {"HTTP_AUTHORIZATION": f"Bearer {ulogin.json()['access']}"}

    cr = c.post(
        "/api/v1/communities/",
        data={"name": "Mod Test", "slug": "mod-test", "description": "", "is_open": True},
        content_type="application/json",
        **uauth,
    )
    assert cr.status_code == 201
    slug = cr.json()["slug"]
    comm_id = cr.json()["id"]

    pr = c.post(
        f"/api/v1/communities/{slug}/posts/",
        data={"body": "hello moderation"},
        content_type="application/json",
        **uauth,
    )
    assert pr.status_code == 201
    post_id = pr.json()["id"]

    alogin = c.post(
        "/api/v1/auth/login/",
        data={"email": "adm-com@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {alogin.json()['access']}"}

    lst = c.get("/api/v1/admin/communities/", **auth)
    assert lst.status_code == 200
    bodies = lst.json()
    assert any(x["id"] == comm_id and x.get("posts_count", 0) >= 1 for x in bodies)

    posts = c.get(f"/api/v1/admin/communities/{comm_id}/posts/", **auth)
    assert posts.status_code == 200
    assert any(p["id"] == post_id for p in posts.json())

    del_r = c.delete(f"/api/v1/admin/communities/posts/{post_id}/", **auth)
    assert del_r.status_code == 204

    patch = c.patch(
        f"/api/v1/admin/communities/{comm_id}/",
        data={"is_open": False, "description": "closed by admin"},
        content_type="application/json",
        **auth,
    )
    assert patch.status_code == 200
    assert patch.json()["is_open"] is False
    assert patch.json()["description"] == "closed by admin"


@pytest.mark.django_db
def test_non_admin_cannot_moderate_communities():
    c = pytest.importorskip("django.test").Client()
    reg = register_user(c, "plain-com@example.com", password="VerySecret1!")
    auth = {"HTTP_AUTHORIZATION": f"Bearer {reg['access']}"}
    assert c.get("/api/v1/admin/communities/", **auth).status_code == 403
