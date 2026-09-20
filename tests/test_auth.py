import time

import jwt
import pytest
from fastapi.testclient import TestClient

from app.auth import ALGORITHM, SECRET_KEY
from tests.conftest import create


def login(client: TestClient, username: str = "auth-user", password: str = "correct-password"):
    return client.post(
        "/auth/login",
        data={"username": username, "password": password},
    )


def test_login_returns_bearer_access_token(client: TestClient):
    create(client, "/users", {"username": "auth-user", "password": "correct-password", "role": "Cashier"})
    response = login(client)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_token_contains_user_claims(client: TestClient):
    user = create(client, "/users", {"username": "claims-user", "password": "correct-password", "role": "Manager"})
    token = login(client, "claims-user").json()["access_token"]
    claims = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert claims["sub"] == "claims-user"
    assert claims["user_id"] == user["id"]
    assert claims["role"] == "Manager"
    assert claims["exp"] > time.time()


@pytest.mark.parametrize(
    ("username", "password"),
    [("missing-user", "password"), ("auth-user", "wrong-password")],
)
def test_login_rejects_invalid_credentials(client: TestClient, username: str, password: str):
    create(client, "/users", {"username": "auth-user", "password": "correct-password"})
    response = login(client, username, password)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_requires_form_fields(client: TestClient):
    assert client.post("/auth/login", data={"username": "missing-password"}).status_code == 422


def test_current_user_requires_bearer_token(client: TestClient):
    response = client.get("/auth/me")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_current_user_returns_authenticated_user(client: TestClient):
    user = create(client, "/users", {"username": "me-user", "password": "correct-password", "role": "Admin"})
    token = login(client, "me-user").json()["access_token"]
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["id"] == user["id"]
    assert response.json()["username"] == "me-user"
    assert response.json()["role"] == "Admin"
    assert "password_hash" not in response.json()


@pytest.mark.parametrize("authorization", ["Bearer invalid-token", "Basic invalid-token", "invalid-header"])
def test_current_user_rejects_invalid_authorization_headers(client: TestClient, authorization: str):
    response = client.get("/auth/me", headers={"Authorization": authorization})
    assert response.status_code == 401


def test_current_user_rejects_expired_token(client: TestClient):
    create(client, "/users", {"username": "expired-user", "password": "correct-password"})
    token = jwt.encode({"sub": "expired-user", "exp": int(time.time()) - 1}, SECRET_KEY, algorithm=ALGORITHM)
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_current_user_rejects_token_for_deleted_user(client: TestClient):
    user = create(client, "/users", {"username": "deleted-user", "password": "correct-password"})
    token = login(client, "deleted-user").json()["access_token"]
    assert client.delete(f"/users/{user['id']}").status_code == 204
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401


def test_openapi_declares_oauth2_bearer_security(client: TestClient):
    schema = client.get("/openapi.json").json()
    assert "OAuth2PasswordBearer" in schema["components"]["securitySchemes"]
    assert schema["paths"]["/auth/me"]["get"]["security"]
    assert schema["paths"]["/auth/admin-check"]["get"]["security"]


def test_admin_can_access_admin_check(client: TestClient):
    create(client, "/users", {"username": "admin-user", "password": "correct-password", "role": "Admin"})
    token = login(client, "admin-user").json()["access_token"]
    response = client.get("/auth/admin-check", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["username"] == "admin-user"


@pytest.mark.parametrize("role", ["Cashier", "Manager"])
def test_non_admin_users_are_forbidden_from_admin_check(client: TestClient, role: str):
    username = f"{role.lower()}-user"
    create(client, "/users", {"username": username, "password": "correct-password", "role": role})
    token = login(client, username).json()["access_token"]
    response = client.get("/auth/admin-check", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"
