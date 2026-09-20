from fastapi.testclient import TestClient


def test_root_healthcheck(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "POS API is running"}


def test_invalid_pagination_parameter_returns_422(client: TestClient):
    assert client.get("/categories?skip=not-an-integer").status_code == 422


def test_empty_collections_return_empty_lists(client: TestClient):
    for path in ("/categories", "/suppliers", "/products", "/customers", "/users", "/sales", "/sale-items", "/payments", "/receipts"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json() == []


def test_large_pagination_window_is_valid(client: TestClient):
    response = client.get("/categories?skip=1000&limit=1000")
    assert response.status_code == 200
    assert response.json() == []


import pytest


@pytest.mark.parametrize("path", ["/categories", "/suppliers", "/products", "/customers", "/users", "/sales", "/sale-items", "/payments", "/receipts"])
def test_collection_endpoints_accept_default_pagination(client: TestClient, path: str):
    response = client.get(f"{path}?skip=0&limit=100")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
