import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User
from tests.conftest import create


def test_user_crud_hashes_password_and_never_returns_it(client: TestClient, db_session: Session):
    user = create(client, "/users", {"username": "manager", "password": "plain-text"})
    assert "password" not in user
    assert "password_hash" not in user
    stored = db_session.query(User).filter(User.id == user["id"]).one()
    assert stored.password_hash != "plain-text"
    assert stored.password_hash.startswith("$2")
    updated = client.put(f"/users/{user['id']}", json={"role": "Manager", "password": "new-secret"})
    assert updated.status_code == 200
    assert updated.json()["role"] == "Manager"
    assert client.delete(f"/users/{user['id']}").status_code == 204


def test_duplicate_username_is_rejected(client: TestClient):
    create(client, "/users", {"username": "duplicate", "password": "secret"})
    duplicate = client.post("/users", json={"username": "duplicate", "password": "another"})
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "Username already exists"


def test_user_validation_and_missing_resource(client: TestClient):
    assert client.post("/users", json={"username": "missing-password"}).status_code == 422
    assert client.get("/users/99999").status_code == 404
    assert client.put("/users/99999", json={"role": "Manager"}).status_code == 404
    assert client.delete("/users/99999").status_code == 404


@pytest.mark.parametrize("role", ["Admin", "Manager", "Cashier"])
def test_each_user_role_is_accepted(client: TestClient, role: str):
    user = create(client, "/users", {"username": role.lower(), "password": "secret", "role": role})
    assert user["role"] == role


def test_invalid_user_role_returns_422(client: TestClient):
    response = client.post("/users", json={"username": "invalid-role", "password": "secret", "role": "Owner"})
    assert response.status_code == 422


def test_user_list_pagination(client: TestClient):
    for index in range(3):
        create(client, "/users", {"username": f"user-{index}", "password": "secret"})
    assert len(client.get("/users?skip=1&limit=2").json()) == 2


@pytest.mark.parametrize("payload", [{"password": "missing username"}, {"username": "missing-password"}, {"username": 123, "password": "secret"}])
def test_user_invalid_payload_variants(client: TestClient, payload: dict):
    assert client.post("/users", json=payload).status_code == 422


@pytest.mark.parametrize("query", ["?skip=abc", "?limit=abc", "?skip=-1"])
def test_user_invalid_pagination_variants(client: TestClient, query: str):
    assert client.get(f"/users{query}").status_code == 422


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_user_missing_resource_for_each_method(client: TestClient, method: str):
    if method == "get":
        response = client.get("/users/98765")
    elif method == "put":
        response = client.put("/users/98765", json={"role": "Manager"})
    else:
        response = client.delete("/users/98765")
    assert response.status_code == 404
