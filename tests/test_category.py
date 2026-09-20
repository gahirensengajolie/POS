from fastapi.testclient import TestClient

from tests.conftest import create


def test_category_crud_and_pagination(client: TestClient):
    category = create(client, "/categories", {"name": "Food", "description": "Food items"})
    assert client.get(f"/categories/{category['id']}").json()["name"] == "Food"

    updated = client.put(
        f"/categories/{category['id']}",
        json={"name": "Packaged Food", "description": "Shelf stable food"},
    )
    assert updated.status_code == 200
    assert updated.json()["name"] == "Packaged Food"
    assert len(client.get("/categories?skip=0&limit=1").json()) == 1

    assert client.delete(f"/categories/{category['id']}").status_code == 204
    assert client.get(f"/categories/{category['id']}").status_code == 404


def test_category_validation_and_missing_resources(client: TestClient):
    assert client.post("/categories", json={}).status_code == 422
    assert client.get("/categories/99999").status_code == 404
    assert client.put("/categories/99999", json={"name": "Missing"}).status_code == 404
    assert client.delete("/categories/99999").status_code == 404


def test_category_list_pagination_returns_requested_window(client: TestClient):
    for name in ("One", "Two", "Three"):
        create(client, "/categories", {"name": name})
    response = client.get("/categories?skip=1&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "Two"


def test_duplicate_category_name_is_rejected(client: TestClient):
    create(client, "/categories", {"name": "Duplicate Category"})
    duplicate = client.post("/categories", json={"name": "Duplicate Category"})
    assert duplicate.status_code == 400
    assert "already exists" in duplicate.json()["detail"]


import pytest


@pytest.mark.parametrize("query", ["?skip=-1", "?limit=0", "?skip=abc", "?limit=abc"])
def test_category_invalid_pagination_inputs(client: TestClient, query: str):
    assert client.get(f"/categories{query}").status_code == 422


@pytest.mark.parametrize("payload", [{"description": "missing name"}, {"name": 123}, {"name": None}])
def test_category_invalid_payload_variants(client: TestClient, payload: dict):
    assert client.post("/categories", json=payload).status_code == 422


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_category_missing_resource_for_each_method(client: TestClient, method: str):
    if method == "get":
        response = client.get("/categories/98765")
    elif method == "put":
        response = client.put("/categories/98765", json={"description": "missing"})
    else:
        response = client.delete("/categories/98765")
    assert response.status_code == 404
