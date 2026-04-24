import pytest
from django.test import Client

from tests.support import register_user


@pytest.mark.django_db
def test_profile_me_dashboard_and_wall():
    c = Client()
    reg = register_user(c, "pw1@example.com", display_name="Wall User")
    access = reg["access"]
    uid = reg["user"]["id"]
    auth = {"HTTP_AUTHORIZATION": f"Bearer {access}"}

    r_d = c.get("/api/v1/profiles/me/dashboard/", **auth)
    assert r_d.status_code == 200
    assert "layout" in r_d.json()

    r_patch = c.patch(
        "/api/v1/profiles/me/dashboard/",
        data={"layout": {"version": 1, "widgets": [{"id": "a", "type": "note", "title": "T", "body": "B"}]}},
        content_type="application/json",
        **auth,
    )
    assert r_patch.status_code == 200
    assert r_patch.json()["layout"]["widgets"][0]["id"] == "a"

    r_me = c.get("/api/v1/profiles/me/", **auth)
    assert r_me.status_code == 200
    assert r_me.json()["email"] == "pw1@example.com"

    r_post = c.post(
        f"/api/v1/walls/{uid}/posts/",
        data={"body": "Привет со стены"},
        content_type="application/json",
        **auth,
    )
    assert r_post.status_code == 201
    body = r_post.json()
    assert body["body"] == "Привет со стены"
    assert "author_display_name" in body

    r_list = c.get(f"/api/v1/walls/{uid}/posts/", **auth)
    assert r_list.status_code == 200
    data = r_list.json()
    assert data["count"] >= 1
    assert len(data["results"]) >= 1
