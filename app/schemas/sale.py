from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.sale import SaleStatus


class SaleBase(BaseModel):
    customer_id: Optional[int] = None
    user_id: int
    total_amount: Decimal
    tax_amount: Decimal
    discount_amount: Decimal = Decimal("0.00")
    final_amount: Decimal
    sale_status: SaleStatus = SaleStatus.completed


class SaleCreate(SaleBase):
    pass


class SaleUpdate(BaseModel):
    customer_id: Optional[int] = None
    total_amount: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    final_amount: Optional[Decimal] = None
    sale_status: Optional[SaleStatus] = None


class SaleOut(SaleBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime