import pytest
from django.contrib.auth import get_user_model
from django.test import Client

from tests.support import register_user

User = get_user_model()


@pytest.mark.django_db
def test_internal_endpoint_requires_internal_employee_or_staff():
    c = Client()
    reg = register_user(c, "partner@example.com")
    auth = {"HTTP_AUTHORIZATION": f"Bearer {reg['access']}"}

    User.objects.filter(pk=reg["user"]["id"]).update(is_employee=True, employment_kind="partner")
    assert c.get("/api/v1/internal/status/", **auth).status_code == 403

    User.objects.filter(pk=reg["user"]["id"]).update(employment_kind="internal")
    assert c.get("/api/v1/internal/status/", **auth).status_code == 200


@pytest.mark.django_db
def test_admin_can_update_employee_kind_and_read_audit():
    c = Client()
    admin_reg = register_user(c, "admin@example.com", password="VerySecret1!")
    User.objects.filter(pk=admin_reg["user"]["id"]).update(is_staff=True, is_superuser=True)
    target_reg = register_user(c, "u@example.com", password="VerySecret1!")
    target = User.objects.get(pk=target_reg["user"]["id"])
    login = c.post(
        "/api/v1/auth/login/",
        data={"email": "admin@example.com", "password": "VerySecret1!"},
        content_type="application/json",
    )
    token = login.json()["access"]
    auth = {"HTTP_AUTHORIZATION": f"Bearer {token}"}

    patch = c.patch(
        "/api/v1/admin/users/",
        data={"id": target.id, "is_employee": True, "employment_kind": "internal"},
        content_type="application/json",
        **auth,
    )
    assert patch.status_code == 200
    target.refresh_from_db()
    assert target.is_employee is True
    assert target.employment_kind == "internal"

    audit = c.get("/api/v1/admin/audit/", **auth)
    assert audit.status_code == 200
    assert len(audit.json()) >= 1
