from fastapi import FastAPI

from app.database import Base, engine
import app.models  # noqa: F401  (ensures all model tables register on Base.metadata)

from app.routers import (
    category,
    supplier,
    product,
    customer,
    user,
    sale,
    sale_item,
    payment,
    receipt,
)

# Create all tables on startup (fine for dev; use Alembic migrations in production)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="POS API", version="1.0.0")

app.include_router(category.router)
app.include_router(supplier.router)
app.include_router(product.router)
app.include_router(customer.router)
app.include_router(user.router)
app.include_router(sale.router)
app.include_router(sale_item.router)
app.include_router(payment.router)
app.include_router(receipt.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "POS API is running"}