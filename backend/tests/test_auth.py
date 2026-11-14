import jwt

from app.configs.settings import get_settings
from app.utils.security import create_access_token


async def test_login_me_password(api):
    response = await api.post(
        "/api/v1/auth/login", json={"email": "admin@example.com", "password": "admin-password-123"}
    )
    assert response.status_code == 200
    assert "password_hash" not in response.text
    token = response.json()["data"]["auth"]["access_token"]
    api.headers["Authorization"] = f"Bearer {token}"
    assert (await api.get("/api/v1/auth/me")).json()["data"]["user"]["id"] == "1"
    wrong = await api.patch(
        "/api/v1/auth/password",
        json={"current_password": "wrong", "new_password": "changed-password-123"},
    )
    assert wrong.status_code == 422
    changed = await api.patch(
        "/api/v1/auth/password",
        json={"current_password": "admin-password-123", "new_password": "changed-password-123"},
    )
    assert changed.status_code == 200
    assert changed.json()["data"] == {}
    assert (
        await api.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "admin-password-123"},
        )
    ).status_code == 401
    assert (
        await api.post(
            "/api/v1/auth/login",
            json={"email": "admin@example.com", "password": "changed-password-123"},
        )
    ).status_code == 200


async def test_role_and_authentication(api):
    api.headers.pop("Authorization")
    response = await api.get("/api/v1/skills")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    for role_id in (2, 3):
        api.headers["Authorization"] = f"Bearer {create_access_token(role_id)}"
        assert (await api.get("/api/v1/skills")).status_code == 403
        assert (await api.get("/api/v1/auth/me")).status_code == 200
    api.headers["Authorization"] = "Bearer invalid-token"
    assert (await api.get("/api/v1/auth/me")).status_code == 401


async def test_inactive_user_and_wrong_audience(api):
    await api.patch("/api/v1/users/2", json={"account_status": "inactive"})
    response = await api.post(
        "/api/v1/auth/login",
        json={"email": "candidate@example.com", "password": "candidate-password-123"},
    )
    assert response.status_code == 401
    api.headers["Authorization"] = f"Bearer {create_access_token(2)}"
    assert (await api.get("/api/v1/auth/me")).status_code == 401
    settings = get_settings()
    claims = jwt.decode(create_access_token(1), options={"verify_signature": False})
    claims["aud"] = "another-app"
    token = jwt.encode(claims, settings.jwt_secret_key.get_secret_value(), algorithm="HS256")
    api.headers["Authorization"] = f"Bearer {token}"
    assert (await api.get("/api/v1/auth/me")).status_code == 401


async def test_login_rate_limit(api):
    for _ in range(get_settings().app_login_rate_limit):
        assert (
            await api.post(
                "/api/v1/auth/login", json={"email": "missing@example.com", "password": "wrong"}
            )
        ).status_code == 401
    response = await api.post(
        "/api/v1/auth/login", json={"email": "missing@example.com", "password": "wrong"}
    )
    assert response.status_code == 429
    assert response.json()["data"] == {}
