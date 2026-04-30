"""Лента и «мои сообщества» (фаза 10+)."""

import pytest
from django.contrib.auth import get_user_model

from apps.communities.models import Community, CommunityMembership, CommunityPost
from apps.social.models import FriendRequest
from apps.walls.models import WallPost

from tests.support import register_user

User = get_user_model()


@pytest.mark.django_db
def test_feed_requires_auth():
    c = pytest.importorskip("django.test").Client()
    assert c.get("/api/v1/social/feed/").status_code in (401, 403)


@pytest.mark.django_db
def test_feed_includes_friend_wall_and_community_posts():
    c = pytest.importorskip("django.test").Client()
    a = register_user(c, "feed-a@example.com", password="VerySecret1!")
    b = register_user(c, "feed-b@example.com", password="VerySecret1!")
    User.objects.filter(pk=a["user"]["id"]).update(display_name="Alice")
    User.objects.filter(pk=b["user"]["id"]).update(display_name="Bob")

    FriendRequest.objects.create(
        from_user_id=a["user"]["id"],
        to_user_id=b["user"]["id"],
        status=FriendRequest.Status.ACCEPTED,
    )

    WallPost.objects.create(
        wall_owner_id=b["user"]["id"],
        author_id=b["user"]["id"],
        body="bob wall hello",
    )

    comm = Community.objects.create(name="Club", slug="club-feed", description="", is_open=True)
    CommunityMembership.objects.create(
        community=comm,
        user_id=a["user"]["id"],
        role=CommunityMembership.Role.MEMBER,
    )
    CommunityPost.objects.create(community=comm, author_id=b["user"]["id"], body="club news")

    login = c.post(
        "/api/v1/auth/login/",
        data={"email": "feed-a@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {login.json()['access']}"}

    r = c.get("/api/v1/social/feed/", **auth)
    assert r.status_code == 200
    body = r.json()
    assert "results" in body
    types = {x["type"] for x in body["results"]}
    assert "wall" in types
    assert "community" in types
    assert any(x.get("body") == "bob wall hello" for x in body["results"])
    assert any(x.get("body") == "club news" for x in body["results"])


@pytest.mark.django_db
def test_communities_mine_lists_only_memberships():
    c = pytest.importorskip("django.test").Client()
    u = register_user(c, "mine-u@example.com", password="VerySecret1!")
    Community.objects.create(name="A", slug="mine-a", description="", is_open=True)
    c2 = Community.objects.create(name="B", slug="mine-b", description="", is_open=True)
    CommunityMembership.objects.create(
        community=c2,
        user_id=u["user"]["id"],
        role=CommunityMembership.Role.MEMBER,
    )

    login = c.post(
        "/api/v1/auth/login/",
        data={"email": "mine-u@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {login.json()['access']}"}
    r = c.get("/api/v1/communities/mine/", **auth)
    assert r.status_code == 200
    slugs = {x["slug"] for x in r.json()["results"]}
    assert slugs == {"mine-b"}
