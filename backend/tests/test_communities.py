import uuid

import pytest
from django.test import Client

from tests.support import register_user


@pytest.mark.django_db
def test_communities_list_guest_and_create_auth():
    c = Client()
    r_guest = c.get("/api/v1/communities/")
    assert r_guest.status_code == 200
    payload = r_guest.json()
    assert "results" in payload

    r_post_anon = c.post(
        "/api/v1/communities/",
        data={"name": "X", "slug": "x-slug", "description": "", "is_open": True},
        content_type="application/json",
    )
    assert r_post_anon.status_code == 403

    slug = f"c-{uuid.uuid4().hex[:12]}"
    reg = register_user(c, f"comm-{uuid.uuid4().hex[:8]}@example.com")
    access = reg["access"]
    r_create = c.post(
        "/api/v1/communities/",
        data={
            "name": "Тестовое",
            "slug": slug,
            "description": "Описание",
            "is_open": True,
        },
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {access}",
    )
    assert r_create.status_code == 201
    assert r_create.json()["slug"] == slug
