from typing import Optional
from decimal import Decimal
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.payment import PaymentMethod


class PaymentBase(BaseModel):
    sale_id: int
    payment_method: PaymentMethod
    amount_paid: Decimal


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    payment_method: Optional[PaymentMethod] = None
    amount_paid: Optional[Decimal] = None


class PaymentOut(PaymentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    processed_at: datetime