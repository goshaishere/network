import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from apps.console.models import UserPermissionGroup
from apps.notifications.models import Notification
from apps.social.models import ContentReport
from apps.walls.models import WallPost
from tests.support import register_user

User = get_user_model()


def grant(user_id: int, *slugs: str):
    group = UserPermissionGroup.objects.create(
        name=f"group-{user_id}",
        slug=f"group-{user_id}",
        permission_slugs=list(slugs),
    )
    group.members.add(user_id)


@pytest.mark.django_db
def test_work_dashboard_requires_slug():
    c = Client()
    reg = register_user(c, "slug-work@example.com")
    User.objects.filter(pk=reg["user"]["id"]).update(is_employee=True)
    auth = {"HTTP_AUTHORIZATION": f"Bearer {reg['access']}"}
    assert c.get("/api/v1/work/dashboard/", **auth).status_code == 403
    grant(reg["user"]["id"], "work.dashboard.read")
    assert c.get("/api/v1/work/dashboard/", **auth).status_code == 200


@pytest.mark.django_db
def test_tasks_filters_and_ordering():
    c = Client()
    reg = register_user(c, "slug-filter@example.com")
    User.objects.filter(pk=reg["user"]["id"]).update(is_employee=True)
    grant(
        reg["user"]["id"],
        "work.group.write",
        "work.group.read",
        "work.board.write",
        "work.board.read",
        "work.column.read",
        "work.task.read",
        "work.task.write",
    )
    auth = {"HTTP_AUTHORIZATION": f"Bearer {reg['access']}"}
    g = c.post("/api/v1/tasks/groups/", {"name": "G", "slug": "g", "description": ""}, content_type="application/json", **auth)
    b = c.post("/api/v1/tasks/boards/", {"group": g.json()["id"], "name": "B", "preset": "generic_pm"}, content_type="application/json", **auth)
    cols = c.get("/api/v1/tasks/columns/", {"board": b.json()["id"]}, **auth).json()
    c.post("/api/v1/tasks/", {"board": b.json()["id"], "column": cols[0]["id"], "title": "Alpha"}, content_type="application/json", **auth)
    c.post("/api/v1/tasks/", {"board": b.json()["id"], "column": cols[0]["id"], "title": "Beta"}, content_type="application/json", **auth)
    r = c.get("/api/v1/tasks/", {"board": b.json()["id"], "q": "Al", "ordering": "-position"}, **auth)
    assert r.status_code == 200
    assert len(r.json()) == 1


@pytest.mark.django_db
def test_moderation_and_notifications_flow():
    c = Client()
    staff = register_user(c, "staff-mod@example.com")
    user = register_user(c, "user-mod@example.com")
    User.objects.filter(pk=staff["user"]["id"]).update(is_staff=True)
    grant(staff["user"]["id"], "moderation.queue.read", "moderation.queue.write")
    grant(user["user"]["id"], "moderation.report.write")
    post = WallPost.objects.create(wall_owner_id=user["user"]["id"], author_id=user["user"]["id"], body="x")
    user_auth = {"HTTP_AUTHORIZATION": f"Bearer {user['access']}"}
    staff_auth = {"HTTP_AUTHORIZATION": f"Bearer {staff['access']}"}
    r = c.post(
        "/api/v1/social/reports/",
        {"target_type": ContentReport.TargetType.WALL_POST, "target_id": post.id, "reason": "spam"},
        content_type="application/json",
        **user_auth,
    )
    assert r.status_code == 201
    assert Notification.objects.filter(user_id=staff["user"]["id"], kind="moderation.report_created").exists()
    list_resp = c.get("/api/v1/admin/moderation/reports/", **staff_auth)
    assert list_resp.status_code == 200
    rid = list_resp.json()[0]["id"]
    patch_resp = c.patch(
        f"/api/v1/admin/moderation/reports/{rid}/",
        {"status": "resolved", "decision": "accepted"},
        content_type="application/json",
        **staff_auth,
    )
    assert patch_resp.status_code == 200
