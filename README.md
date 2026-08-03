# POS API

A REST API for a Point of Sale (POS) system, built with **FastAPI**, **SQLAlchemy**, and **PostgreSQL**, using a layered **models → repositories → services → routers** architecture with Pydantic **schemas** for request/response validation.

## Project Description

This API models a simple retail point-of-sale workflow:

- **Categories** and **Suppliers** organize and source **Products**.
- Each **Product** has a corresponding **Inventory** record that tracks stock on hand.
- **Customers** make purchases, which are recorded as **Sales**, processed by a **User** (cashier/staff).
- Each **Sale** is made up of one or more **Sale Items**, each referencing a **Product**. Adding a sale item automatically decrements the product's inventory and recalculates the sale's total.
- **Payments** are recorded against a **Sale** (a sale can have multiple payments — e.g. split payment).
- A **Receipt** is issued for a completed **Sale**.

Invalid records are rejected before they ever hit the database — for example, you cannot create a sale item for a product or sale that doesn't exist, and stock levels are checked before a sale reduces inventory.

## Architecture

Each entity is implemented across four layers, keeping responsibilities separated:

```
Router      → HTTP layer only: path/query params, request body, calls the service, returns the response
Service     → business rules: existence checks, uniqueness checks, stock validation, total recalculation
Repository  → pure data access: SQLAlchemy queries only, no validation, no HTTP concerns
Model       → SQLAlchemy ORM table definition + relationships
Schema      → Pydantic request/response validation
```

Request flow: `Router → Service → Repository → Database`, and the response flows back up, serialized by the Pydantic schema set as the route's `response_model`.

## Entity-Relationship Overview

```
Category (1) ──< (many) Product
Supplier (1) ──< (many) Product
Product  (1) ──1 (1)    Inventory
Customer (1) ──< (many) Sale
User     (1) ──< (many) Sale        (the cashier who processed the sale)
Sale     (1) ──< (many) SaleItem
Product  (1) ──< (many) SaleItem
Sale     (1) ──< (many) Payment
Sale     (1) ──1 (1)    Receipt
```

## Project Structure

```
pos_backend/
├── app/
│   ├── main.py                 # FastAPI app, includes all routers, creates tables
│   ├── database.py             # engine, session, base, get_db dependency
│   ├── models/                 # SQLAlchemy ORM models (one file per entity)
│   ├── schemas/                # Pydantic request/response schemas
│   ├── repositories/           # Raw DB access (get/create/update/delete queries)
│   ├── services/                # Business rules & validation, calls repositories
│   ├── routers/                 # FastAPI endpoints, calls services
│   └── utils/
│       └── security.py         # Password hashing helpers (bcrypt)
├── requirements.txt
├── .env.example
└── README.md
```

## Tech Stack

- **FastAPI** — web framework & automatic OpenAPI/Swagger docs
- **SQLAlchemy** (ORM) — models & relationships
- **PostgreSQL** — database
- **Pydantic** — request/response validation
- **Passlib (bcrypt)** — password hashing for the `User` entity
- **Uvicorn** — ASGI server

## Setup Instructions

### 1. Prerequisites

- Python 3.10+
- PostgreSQL running locally or accessible remotely

### 2. Install dependencies

```bash
git clone <your-repo-url>
cd pos_backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure the database

```sql
CREATE DATABASE pos_db;
```

```bash
cp .env.example .env
# then edit .env:
# DATABASE_URL=postgresql://<user>:<password>@localhost:5432/pos_db
```

### 4. Run the API

From the project root (the folder containing `app/`):

```bash
fastapi dev app/main.py
```

or, with uvicorn directly:

```bash
uvicorn app.main:app --reload
```

> `fastapi dev`/`fastapi run` expect a **file path** as their argument (e.g. `app/main.py`), not a bare word like `dev`. Running `fastapi run dev` will fail with "Path does not exist" because it tries to treat `dev` itself as the path.

On startup, `base.metadata.create_all()` creates every table that doesn't already exist, based on the SQLAlchemy models. (For production, prefer Alembic migrations instead.)

### 5. Open the docs

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API Endpoints

| Resource     | Base Path       | Notes |
|--------------|------------------|-------|
| Categories   | `/categories`    | Unique `name` |
| Suppliers    | `/suppliers`     | |
| Products     | `/products`      | Validates `category_id` / `supplier_id`; unique `sku`; filter by `category_id`, `supplier_id`, `is_active` |
| Customers    | `/customers`     | Unique `email` |
| Users        | `/users`         | Unique `username` / `email`; password hashed with bcrypt, never returned |
| Inventory    | `/inventory`     | One record per product; validates `product_id` |
| Sales        | `/sales`         | Validates `customer_id` / `user_id`; deleting a sale restores stock for its items |
| Sale Items   | `/sale-items`    | Validates `sale_id` / `product_id`; checks stock; decrements inventory and recalculates the parent sale's `total_amount` |
| Payments     | `/payments`      | Validates `sale_id` |
| Receipts     | `/receipts`      | Validates `sale_id`; one receipt per sale; unique `receipt_number` |

Each resource supports:

- `POST   /resource`        → create (`201 Created`)
- `GET    /resource`        → list all (`200 OK`, supports `skip`/`limit` pagination)
- `GET    /resource/{id}`   → get one (`200 OK`, or `404` if not found)
- `PUT    /resource/{id}`   → update (`200 OK`, or `404` if not found)
- `DELETE /resource/{id}`   → delete (`204 No Content`, or `404` if not found)

## Data Validation & Integrity Rules

- Pydantic schemas validate all request bodies (types, required fields, string lengths, positive numbers, valid emails, enum values, etc.) at the router boundary.
- Services check that referenced foreign keys exist before writing to the database, returning `400 Bad Request` with a descriptive message if not (e.g. creating a product with a `category_id` that doesn't exist).
- Duplicate values on fields expected to be unique (category name, product SKU, user username/email, customer email, receipt number) are rejected with `400 Bad Request`.
- Requesting, updating, or deleting a record by an ID that doesn't exist returns `404 Not Found`.
- Creating a sale item checks available stock in `Inventory` first, and keeps inventory and the sale's `total_amount` in sync as items are added, updated, or removed.

## Testing the API

Test every endpoint using **Swagger UI** (`/docs`) or **Postman**. A typical end-to-end flow:

1. **Create reference data:** `POST /categories`, `POST /suppliers`, `POST /customers`, `POST /users`.
2. **Create a product:** `POST /products` referencing the category/supplier IDs.
3. **Stock the product:** `POST /inventory` with the product's ID and starting `quantity_on_hand`.
4. **Open a sale:** `POST /sales` referencing the customer and user IDs.
5. **Add sale items:** `POST /sale-items` — confirm inventory decreases and the sale's `total_amount` updates (`GET /sales/{id}`).
6. **Record a payment:** `POST /payments` referencing the sale.
7. **Issue a receipt:** `POST /receipts` referencing the sale.
8. **Retrieve all / one:** `GET` each collection and a single record by ID.
9. **Update a record:** `PUT` an existing record (e.g. change a product's price, a sale's status).
10. **Delete a record:** `DELETE` a record, then confirm a subsequent `GET` returns `404`.
11. **Negative tests:**
    - `GET/PUT/DELETE` an ID that doesn't exist → `404`.
    - `POST` a sale item with a non-existent `product_id`/`sale_id` → `400`.
    - `POST` a product with a duplicate `sku`, or a category with a duplicate `name` → `400`.
    - `POST` invalid data (negative `price`, missing required field, malformed email) → `422`.
    - `POST` a sale item with `quantity` greater than available stock → `400`.

## Notes

- Authentication/authorization (login, JWT) is out of scope; `User` stores bcrypt-hashed passwords but there's no login endpoint.
- `base.metadata.create_all()` is used for simplicity instead of Alembic migrations.
