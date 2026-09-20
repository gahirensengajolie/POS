from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    """Provide a fresh in-memory SQLite database for every test."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """Override the production database dependency with the test-only SQLite session."""
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create(client: TestClient, path: str, payload: dict) -> dict:
    response = client.post(path, json=payload)
    assert response.status_code == 201, response.text
    return response.json()


@pytest.fixture()
def reference_data(client: TestClient) -> dict:
    """Create the records needed by products, sales, payments, and receipts."""
    category = create(client, "/categories", {"name": "Beverages", "description": "Drinks"})
    supplier = create(
        client,
        "/suppliers",
        {
            "company_name": "Acme Wholesale",
            "contact_name": "Alex Supplier",
            "phone": "555-0100",
            "email": "supplier@example.com",
        },
    )
    customer = create(
        client,
        "/customers",
        {
            "first_name": "Casey",
            "last_name": "Customer",
            "email": "casey@example.com",
            "phone": "555-0101",
        },
    )
    user = create(
        client,
        "/users",
        {"username": "cashier", "password": "secret-password", "role": "Cashier"},
    )
    product = create(
        client,
        "/products",
        {
            "sku": "COF-001",
            "name": "Coffee",
            "description": "Ground coffee",
            "price": "4.50",
            "cost_price": "2.00",
            "stock_quantity": 20,
            "category_id": category["id"],
            "supplier_id": supplier["id"],
        },
    )
    sale = create(
        client,
        "/sales",
        {
            "customer_id": customer["id"],
            "user_id": user.get("id", 1),
            "total_amount": "4.50",
            "tax_amount": "0.45",
            "discount_amount": "0.00",
            "final_amount": "4.95",
            "sale_status": "Completed",
        },
    )
    return {
        "category": category,
        "supplier": supplier,
        "customer": customer,
        "user": user,
        "product": product,
        "sale": sale,
    }
