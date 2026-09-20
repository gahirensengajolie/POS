import pytest
from fastapi.testclient import TestClient

from tests.conftest import create


def test_sale_crud(client: TestClient, reference_data: dict):
    sale = reference_data["sale"]
    assert client.get(f"/sales/{sale['id']}").json()["final_amount"] == "4.95"
    updated = client.put(f"/sales/{sale['id']}", json={"sale_status": "Refunded"})
    assert updated.status_code == 200
    assert updated.json()["sale_status"] == "Refunded"
    assert client.delete(f"/sales/{sale['id']}").status_code == 204


def test_sale_validation_and_missing_resource(client: TestClient):
    invalid = {"user_id": 1, "total_amount": "1.00", "tax_amount": "0.10", "final_amount": "1.10", "sale_status": "NotAStatus"}
    assert client.post("/sales", json=invalid).status_code == 422
    assert client.get("/sales/99999").status_code == 404
    assert client.put("/sales/99999", json={"sale_status": "Refunded"}).status_code == 404
    assert client.delete("/sales/99999").status_code == 404


@pytest.mark.parametrize("status", ["Completed", "Refunded", "Canceled"])
def test_each_sale_status_is_accepted(client: TestClient, reference_data: dict, status: str):
    sale = create(client, "/sales", {"user_id": reference_data["user"]["id"], "total_amount": "2.00", "tax_amount": "0.20", "final_amount": "2.20", "sale_status": status})
    assert sale["sale_status"] == status


def test_sale_can_have_no_customer(client: TestClient, reference_data: dict):
    sale = create(client, "/sales", {"user_id": reference_data["user"]["id"], "total_amount": "1.00", "tax_amount": "0.10", "final_amount": "1.10"})
    assert sale["customer_id"] is None


def test_sale_list_pagination(client: TestClient, reference_data: dict):
    for index in range(3):
        create(client, "/sales", {"user_id": reference_data["user"]["id"], "total_amount": str(index + 1), "tax_amount": "0.10", "final_amount": str(index + 1.1)})
    assert len(client.get("/sales?skip=1&limit=2").json()) == 2


@pytest.mark.parametrize("payload", [{"total_amount": "1", "tax_amount": "0", "final_amount": "1"}, {"user_id": 1, "tax_amount": "0", "final_amount": "1"}, {"user_id": 1, "total_amount": "1", "final_amount": "1"}, {"user_id": 1, "total_amount": "1", "tax_amount": "0"}])
def test_sale_missing_required_field_variants(client: TestClient, payload: dict):
    assert client.post("/sales", json=payload).status_code == 422


@pytest.mark.parametrize("query", ["?skip=abc", "?limit=abc", "?skip=-1"])
def test_sale_invalid_pagination_variants(client: TestClient, query: str):
    assert client.get(f"/sales{query}").status_code == 422


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_sale_missing_resource_for_each_method(client: TestClient, method: str):
    if method == "get":
        response = client.get("/sales/98765")
    elif method == "put":
        response = client.put("/sales/98765", json={"sale_status": "Canceled"})
    else:
        response = client.delete("/sales/98765")
    assert response.status_code == 404
