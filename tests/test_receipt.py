from fastapi.testclient import TestClient

from tests.conftest import create


def test_receipt_crud(client: TestClient, reference_data: dict):
    receipt = create(client, "/receipts", {"sale_id": reference_data["sale"]["id"], "receipt_number": "R-1001"})
    assert client.get(f"/receipts/{receipt['id']}").status_code == 200
    updated = client.put(f"/receipts/{receipt['id']}", json={"receipt_number": "R-1002"})
    assert updated.status_code == 200
    assert client.delete(f"/receipts/{receipt['id']}").status_code == 204


def test_receipt_validation_and_missing_resource(client: TestClient):
    assert client.post("/receipts", json={"sale_id": 1}).status_code == 422
    assert client.get("/receipts/99999").status_code == 404
    assert client.put("/receipts/99999", json={"receipt_number": "Missing"}).status_code == 404
    assert client.delete("/receipts/99999").status_code == 404


def test_receipt_list_pagination(client: TestClient, reference_data: dict):
    for index in range(3):
        sale = create(client, "/sales", {"user_id": reference_data["user"]["id"], "total_amount": "1.00", "tax_amount": "0.10", "final_amount": "1.10"})
        create(client, "/receipts", {"sale_id": sale["id"], "receipt_number": f"PAGE-{index}"})
    assert len(client.get("/receipts?skip=1&limit=2").json()) == 2


def test_receipt_number_can_be_updated_without_changing_sale(client: TestClient, reference_data: dict):
    receipt = create(client, "/receipts", {"sale_id": reference_data["sale"]["id"], "receipt_number": "ORIGINAL"})
    updated = client.put(f"/receipts/{receipt['id']}", json={"receipt_number": "UPDATED"})
    assert updated.json()["sale_id"] == reference_data["sale"]["id"]
    assert updated.json()["receipt_number"] == "UPDATED"


import pytest


@pytest.mark.parametrize("payload", [{"receipt_number": "MISSING-SALE"}, {"sale_id": 1}, {"sale_id": "bad", "receipt_number": "BAD"}])
def test_receipt_invalid_payload_variants(client: TestClient, payload: dict):
    assert client.post("/receipts", json=payload).status_code == 422


@pytest.mark.parametrize("query", ["?skip=abc", "?limit=abc", "?skip=-1"])
def test_receipt_invalid_pagination_variants(client: TestClient, query: str):
    assert client.get(f"/receipts{query}").status_code == 422


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_receipt_missing_resource_for_each_method(client: TestClient, method: str):
    if method == "get":
        response = client.get("/receipts/98765")
    elif method == "put":
        response = client.put("/receipts/98765", json={"receipt_number": "Missing"})
    else:
        response = client.delete("/receipts/98765")
    assert response.status_code == 404
