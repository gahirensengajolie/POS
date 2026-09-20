from fastapi.testclient import TestClient

from tests.conftest import create


def test_supplier_crud(client: TestClient):
    supplier = create(client, "/suppliers", {"company_name": "Northwind", "phone": "555-0102"})
    assert client.get("/suppliers").json()[0]["company_name"] == "Northwind"
    updated = client.put(f"/suppliers/{supplier['id']}", json={"phone": "555-0103"})
    assert updated.status_code == 200
    assert updated.json()["phone"] == "555-0103"
    assert client.delete(f"/suppliers/{supplier['id']}").status_code == 204


def test_supplier_validation_and_missing_resource(client: TestClient):
    assert client.post("/suppliers", json={"company_name": "Missing Phone"}).status_code == 422
    assert client.get("/suppliers/99999").status_code == 404
    assert client.put("/suppliers/99999", json={"phone": "555"}).status_code == 404
    assert client.delete("/suppliers/99999").status_code == 404


def test_supplier_optional_fields_are_supported(client: TestClient):
    supplier = create(client, "/suppliers", {"company_name": "Minimal Supplier", "phone": "555-0104"})
    assert supplier["contact_name"] is None
    assert supplier["email"] is None


def test_supplier_update_can_change_all_optional_fields(client: TestClient):
    supplier = create(client, "/suppliers", {"company_name": "Old Name", "phone": "555-0105"})
    updated = client.put(
        f"/suppliers/{supplier['id']}",
        json={"company_name": "New Name", "contact_name": "Contact", "phone": "555-0106", "email": "new@example.com"},
    )
    assert updated.status_code == 200
    assert updated.json()["company_name"] == "New Name"
    assert updated.json()["contact_name"] == "Contact"
    assert updated.json()["email"] == "new@example.com"


def test_supplier_list_pagination(client: TestClient):
    for index in range(3):
        create(client, "/suppliers", {"company_name": f"Supplier {index}", "phone": f"555-01{index:02d}"})
    assert len(client.get("/suppliers?skip=1&limit=1").json()) == 1


import pytest


@pytest.mark.parametrize("payload", [{"phone": "missing company"}, {"company_name": "Missing Phone"}, {"company_name": 123, "phone": "555"}])
def test_supplier_invalid_payload_variants(client: TestClient, payload: dict):
    assert client.post("/suppliers", json=payload).status_code == 422


@pytest.mark.parametrize("query", ["?skip=abc", "?limit=abc", "?skip=-1"])
def test_supplier_invalid_pagination_variants(client: TestClient, query: str):
    assert client.get(f"/suppliers{query}").status_code == 422


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_supplier_missing_resource_for_each_method(client: TestClient, method: str):
    if method == "get":
        response = client.get("/suppliers/98765")
    elif method == "put":
        response = client.put("/suppliers/98765", json={"phone": "555"})
    else:
        response = client.delete("/suppliers/98765")
    assert response.status_code == 404
