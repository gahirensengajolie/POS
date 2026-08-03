from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, ConfigDict


class SaleItemBase(BaseModel):
    sale_id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal


class SaleItemCreate(SaleItemBase):
    pass


class SaleItemUpdate(BaseModel):
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    subtotal: Optional[Decimal] = None


class SaleItemOut(SaleItemBase):
    model_config = ConfigDict(from_attributes=True)
    id: int