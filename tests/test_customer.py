from fastapi.testclient import TestClient

from tests.conftest import create


def test_customer_crud(client: TestClient):
    customer = create(client, "/customers", {"first_name": "Taylor", "last_name": "Buyer", "email": "taylor@example.com"})
    assert client.get(f"/customers/{customer['id']}").status_code == 200
    updated = client.put(f"/customers/{customer['id']}", json={"last_name": "Loyal Buyer"})
    assert updated.status_code == 200
    assert updated.json()["last_name"] == "Loyal Buyer"
    assert client.delete(f"/customers/{customer['id']}").status_code == 204


def test_customer_validation_and_missing_resource(client: TestClient):
    assert client.post("/customers", json={"first_name": "Only First Name"}).status_code == 422
    assert client.get("/customers/99999").status_code == 404
    assert client.put("/customers/99999", json={"last_name": "Missing"}).status_code == 404
    assert client.delete("/customers/99999").status_code == 404


def test_customer_supports_minimal_and_full_contact_data(client: TestClient):
    minimal = create(client, "/customers", {"first_name": "Minimal", "last_name": "Customer"})
    assert minimal["email"] is None
    assert minimal["phone"] is None
    full = create(client, "/customers", {"first_name": "Full", "last_name": "Customer", "email": "full@example.com", "phone": "555-0110"})
    assert full["email"] == "full@example.com"
    assert full["phone"] == "555-0110"


def test_customer_list_pagination(client: TestClient):
    for index in range(3):
        create(client, "/customers", {"first_name": f"Customer{index}", "last_name": "Test"})
    response = client.get("/customers?skip=1&limit=2")
    assert response.status_code == 200
    assert len(response.json()) == 2


import pytest


@pytest.mark.parametrize("payload", [{"last_name": "missing first"}, {"first_name": "missing last"}, {"first_name": 123, "last_name": "Customer"}])
def test_customer_invalid_payload_variants(client: TestClient, payload: dict):
    assert client.post("/customers", json=payload).status_code == 422


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_customer_missing_resource_for_each_method(client: TestClient, method: str):
    if method == "get":
        response = client.get("/customers/98765")
    elif method == "put":
        response = client.put("/customers/98765", json={"last_name": "Missing"})
    else:
        response = client.delete("/customers/98765")
    assert response.status_code == 404
