import pytest

from app.configs.settings import get_settings


@pytest.mark.parametrize("role", ["candidate", "employer"])
async def test_public_registration_and_login(api, role):
    api.headers.pop("Authorization")
    payload = {
        "name": " New user ",
        "email": f"New-{role}@example.com",
        "password": "new-password-123  ",
        "account_type": role,
    }
    response = await api.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201, response.text
    body = response.json()
    assert set(body) == {"message", "error", "data"}
    assert set(body["data"]) == {"user"}
    user = body["data"]["user"]
    assert user["name"] == "New user"
    assert user["email"] == payload["email"].lower()
    assert user["account_type"] == role
    assert user["account_status"] == "active"
    assert isinstance(user["id"], str)
    assert "password" not in user and "password_hash" not in user
    login = await api.post(
        "/api/v1/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"],
        },
    )
    assert login.status_code == 200
    api.headers["Authorization"] = f"Bearer {login.json()['data']['auth']['access_token']}"
    assert (await api.get("/api/v1/users")).status_code == 403


async def test_duplicate_registration(api):
    payload = {
        "name": "Duplicate",
        "email": "ADMIN@example.com",
        "password": "new-password-123",
        "account_type": "candidate",
    }
    response = await api.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["data"] == {}
    assert "user" in response.json()["error"]


@pytest.mark.parametrize(
    "change",
    [
        {"account_type": "admin"},
        {"account_status": "active"},
        {"password": "short"},
        {"email": "invalid"},
        {"name": "   "},
    ],
)
async def test_registration_rejects_invalid_or_privileged_input(api, change):
    payload = {
        "name": "User",
        "email": "new@example.com",
        "password": "new-password-123",
        "account_type": "candidate",
        **change,
    }
    response = await api.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422
    assert response.json()["data"] == {}


async def test_registration_rate_limit_is_separate(api):
    for _ in range(get_settings().app_register_rate_limit):
        response = await api.post("/api/v1/auth/register", json={})
        assert response.status_code == 422
    assert (await api.post("/api/v1/auth/register", json={})).status_code == 429
    login = await api.post(
        "/api/v1/auth/login",
        json={
            "email": "admin@example.com",
            "password": "admin-password-123",
        },
    )
    assert login.status_code == 200
