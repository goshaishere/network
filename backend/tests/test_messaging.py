import pytest
from django.test import Client

from tests.support import register_user


@pytest.mark.django_db
def test_messaging_conversation_messages_and_privacy():
    c = Client()
    u1 = register_user(c, "m1@example.com", display_name="Alice")
    u2 = register_user(c, "m2@example.com", display_name="Bob")
    u3 = register_user(c, "m3@example.com", display_name="Carol")

    a1 = u1["access"]
    a3 = u3["access"]
    id2 = u2["user"]["id"]

    r_create = c.post(
        "/api/v1/messaging/conversations/",
        data={"participant_id": id2},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {a1}",
    )
    assert r_create.status_code in (200, 201)
    conv = r_create.json()
    cid = conv["id"]
    assert conv["other_user_id"] == id2
    assert conv.get("other_display_name") == "Bob"

    r_list = c.get("/api/v1/messaging/conversations/", HTTP_AUTHORIZATION=f"Bearer {a1}")
    assert r_list.status_code == 200
    listed = r_list.json()
    assert isinstance(listed, list)
    assert any(x["id"] == cid for x in listed)

    r_msg = c.post(
        f"/api/v1/messaging/conversations/{cid}/messages/",
        data={"body": "Привет"},
        content_type="application/json",
        HTTP_AUTHORIZATION=f"Bearer {a1}",
    )
    assert r_msg.status_code == 201
    mid = r_msg.json()["id"]

    r_hist = c.get(f"/api/v1/messaging/conversations/{cid}/messages/", HTTP_AUTHORIZATION=f"Bearer {a1}")
    assert r_hist.status_code == 200
    hist = r_hist.json()
    assert "results" in hist
    assert any(m["id"] == mid for m in hist["results"])

    r_forbidden = c.get(
        f"/api/v1/messaging/conversations/{cid}/messages/",
        HTTP_AUTHORIZATION=f"Bearer {a3}",
    )
    assert r_forbidden.status_code == 403
