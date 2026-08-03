from typing import Optional
from pydantic import BaseModel, ConfigDict


class SupplierBase(BaseModel):
    company_name: str
    contact_name: Optional[str] = None
    phone: str
    email: Optional[str] = None


class SupplierCreate(SupplierBase):
    pass


class SupplierUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None


class SupplierOut(SupplierBase):
    model_config = ConfigDict(from_attributes=True)
    id: int