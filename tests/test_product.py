from decimal import Decimal

from fastapi.testclient import TestClient

from tests.conftest import create


def test_product_crud_and_category_filter(client: TestClient, reference_data: dict):
    category = reference_data["category"]
    supplier = reference_data["supplier"]
    product = create(client, "/products", {"sku": "TEA-002", "name": "Tea", "price": "3.25", "cost_price": "1.25", "category_id": category["id"], "supplier_id": supplier["id"]})
    filtered = client.get(f"/products?category_id={category['id']}")
    assert {row["sku"] for row in filtered.json()} == {"COF-001", "TEA-002"}
    updated = client.put(f"/products/{product['id']}", json={"price": "3.50", "stock_quantity": 8})
    assert updated.status_code == 200
    assert Decimal(updated.json()["price"]) == Decimal("3.50")
    assert client.delete(f"/products/{product['id']}").status_code == 204


def test_product_validation_and_missing_resource(client: TestClient, reference_data: dict):
    invalid = {"sku": "BAD-001", "name": "Invalid price", "price": "not-a-number", "cost_price": "1.00", "category_id": reference_data["category"]["id"]}
    assert client.post("/products", json=invalid).status_code == 422
    assert client.get("/products/99999").status_code == 404
    assert client.put("/products/99999", json={"name": "Missing"}).status_code == 404
    assert client.delete("/products/99999").status_code == 404


def test_duplicate_product_sku_is_rejected(client: TestClient, reference_data: dict):
    payload = {"sku": "DUP-001", "name": "First", "price": "1.00", "cost_price": "0.50", "category_id": reference_data["category"]["id"]}
    create(client, "/products", payload)
    duplicate = client.post("/products", json={**payload, "name": "Second"})
    assert duplicate.status_code == 400
    assert duplicate.json()["detail"] == "SKU already exists"


def test_product_without_supplier_is_supported(client: TestClient, reference_data: dict):
    product = create(client, "/products", {"sku": "NOSUP-001", "name": "Independent", "price": "2.00", "cost_price": "1.00", "category_id": reference_data["category"]["id"]})
    assert product["supplier_id"] is None


def test_product_list_pagination(client: TestClient, reference_data: dict):
    for index in range(3):
        create(client, "/products", {"sku": f"PAGE-{index}", "name": f"Product {index}", "price": "2.00", "cost_price": "1.00", "category_id": reference_data["category"]["id"]})
    assert len(client.get("/products?skip=1&limit=2").json()) == 2


import pytest


@pytest.mark.parametrize("payload", [{"name": "Missing SKU", "price": "1", "cost_price": "1", "category_id": 1}, {"sku": "MISSING-NAME", "price": "1", "cost_price": "1", "category_id": 1}, {"sku": "BAD-PRICE", "name": "Bad", "price": "nope", "cost_price": "1", "category_id": 1}, {"sku": "BAD-COST", "name": "Bad", "price": "1", "cost_price": "nope", "category_id": 1}])
def test_product_invalid_payload_variants(client: TestClient, payload: dict):
    assert client.post("/products", json=payload).status_code == 422


@pytest.mark.parametrize("query", ["?skip=abc", "?limit=abc", "?skip=-1"])
def test_product_invalid_pagination_variants(client: TestClient, query: str):
    assert client.get(f"/products{query}").status_code == 422


@pytest.mark.parametrize("method", ["get", "put", "delete"])
def test_product_missing_resource_for_each_method(client: TestClient, method: str):
    if method == "get":
        response = client.get("/products/98765")
    elif method == "put":
        response = client.put("/products/98765", json={"name": "Missing"})
    else:
        response = client.delete("/products/98765")
    assert response.status_code == 404
