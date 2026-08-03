from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class ReceiptBase(BaseModel):
    sale_id: int
    receipt_number: str


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptUpdate(BaseModel):
    receipt_number: Optional[str] = None


class ReceiptOut(ReceiptBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    issued_at: datetime