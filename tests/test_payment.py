import pytest
from fastapi.testclient import TestClient

from tests.conftest import create


def test_payment_crud(client: TestClient, reference_data: dict):
    payment = create(client, "/payments", {"sale_id": reference_data["sale"]["id"], "payment_method": "Cash", "amount_paid": "4.95"})
    updated = client.put(f"/payments/{payment['id']}", json={"amount_paid": "5.00"})
    assert updated.status_code == 200
    assert updated.json()["amount_paid"] == "5.00"
    assert client.delete(f"/payments/{payment['id']}").status_code == 204


def test_payment_validation_and_missing_resource(client: TestClient):
    invalid = {"sale_id": 1, "payment_method": "NotA method", "amount_paid": "1.00"}
    assert client.post("/payments", json=invalid).status_code == 422
    assert client.get("/payments/99999").status_code == 404
    assert client.put("/payments/99999", json={"amount_paid": "2.00"}).status_code == 404
    assert client.delete("/payments/99999").status_code == 404


@pytest.mark.parametrize("method", ["Cash", "Card", "Mobile", "Split"])
def test_each_payment_method_is_accepted(client: TestClient, reference_data: dict, method: str):
    payment = create(client, "/payments", {"sale_id": reference_data["sale"]["id"], "payment_method": method, "amount_paid": "1.00"})
    assert payment["payment_method"] == method


def test_payment_list_pagination(client: TestClient, reference_data: dict):
    for index in range(3):
        create(client, "/payments", {"sale_id": reference_data["sale"]["id"], "payment_method": "Cash", "amount_paid": str(index + 1)})
    assert len(client.get("/payments?skip=1&limit=2").json()) == 2


@pytest.mark.parametrize("payload", [{"payment_method": "Cash", "amount_paid": "1"}, {"sale_id": 1, "amount_paid": "1"}, {"sale_id": 1, "payment_method": "Cash"}, {"sale_id": 1, "payment_method": "Unknown", "amount_paid": "1"}])
def test_payment_invalid_payload_variants(client: TestClient, payload: dict):
    assert client.post("/payments", json=payload).status_code == 422


@pytest.mark.parametrize("query", ["?skip=abc", "?limit=abc", "?skip=-1"])
def test_payment_invalid_pagination_variants(client: TestClient, query: str):
    assert client.get(f"/payments{query}").status_code == 422


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_payment_missing_resource_for_each_method(client: TestClient, method: str):
    if method == "get":
        response = client.get("/payments/98765")
    elif method == "put":
        response = client.put("/payments/98765", json={"amount_paid": "2"})
    else:
        response = client.delete("/payments/98765")
    assert response.status_code == 404
