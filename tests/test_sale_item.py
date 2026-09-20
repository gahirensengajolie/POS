from fastapi.testclient import TestClient

from tests.conftest import create


def test_sale_item_crud_and_by_sale_lookup(client: TestClient, reference_data: dict):
    sale_id = reference_data["sale"]["id"]
    product_id = reference_data["product"]["id"]
    item = create(client, "/sale-items", {"sale_id": sale_id, "product_id": product_id, "quantity": 2, "unit_price": "4.50", "subtotal": "9.00"})
    by_sale = client.get(f"/sale-items/by-sale/{sale_id}")
    assert [row["id"] for row in by_sale.json()] == [item["id"]]
    updated = client.put(f"/sale-items/{item['id']}", json={"quantity": 3, "unit_price": "5.00", "subtotal": "15.00"})
    assert updated.status_code == 200
    assert updated.json()["quantity"] == 3
    assert client.delete(f"/sale-items/{item['id']}").status_code == 204


def test_sale_item_validation_and_missing_resource(client: TestClient):
    invalid = {"sale_id": "not-an-integer", "product_id": 1, "quantity": 1, "unit_price": "1.00", "subtotal": "1.00"}
    assert client.post("/sale-items", json=invalid).status_code == 422
    assert client.get("/sale-items/99999").status_code == 404
    assert client.put("/sale-items/99999", json={"quantity": 2}).status_code == 404
    assert client.delete("/sale-items/99999").status_code == 404
    assert client.get("/sale-items/by-sale/not-an-integer").status_code == 422


def test_sale_items_by_sale_returns_empty_list_for_unknown_sale(client: TestClient):
    response = client.get("/sale-items/by-sale/99999")
    assert response.status_code == 200
    assert response.json() == []


def test_sale_item_list_pagination(client: TestClient, reference_data: dict):
    for quantity in (1, 2, 3):
        create(client, "/sale-items", {"sale_id": reference_data["sale"]["id"], "product_id": reference_data["product"]["id"], "quantity": quantity, "unit_price": "1.00", "subtotal": str(quantity)})
    assert len(client.get("/sale-items?skip=1&limit=2").json()) == 2


import pytest


@pytest.mark.parametrize("payload", [{"product_id": 1, "quantity": 1, "unit_price": "1", "subtotal": "1"}, {"sale_id": 1, "quantity": 1, "unit_price": "1", "subtotal": "1"}, {"sale_id": 1, "product_id": 1, "unit_price": "1", "subtotal": "1"}, {"sale_id": 1, "product_id": 1, "quantity": 1, "subtotal": "1"}])
def test_sale_item_missing_required_field_variants(client: TestClient, payload: dict):
    assert client.post("/sale-items", json=payload).status_code == 422


@pytest.mark.parametrize("query", ["?skip=abc", "?limit=abc", "?skip=-1"])
def test_sale_item_invalid_pagination_variants(client: TestClient, query: str):
    assert client.get(f"/sale-items{query}").status_code == 422


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_sale_item_missing_resource_for_each_method(client: TestClient, method: str):
    if method == "get":
        response = client.get("/sale-items/98765")
    elif method == "put":
        response = client.put("/sale-items/98765", json={"quantity": 2})
    else:
        response = client.delete("/sale-items/98765")
    assert response.status_code == 404
