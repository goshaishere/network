from django.test import Client


def register_user(
    client: Client,
    email: str,
    *,
    password: str = "VerySecret1!",
    display_name: str = "Tester",
) -> dict:
    r = client.post(
        "/api/v1/auth/register/",
        data={
            "email": email,
            "display_name": display_name,
            "password": password,
            "password_confirm": password,
        },
        content_type="application/json",
    )
    assert r.status_code == 201, r.content
    return r.json()
