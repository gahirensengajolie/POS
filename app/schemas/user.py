from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.models.user import UserRole


class UserBase(BaseModel):
    username: str
    role: UserRole = UserRole.cashier


class UserCreate(UserBase):
    password: str  # plain password in, hashed before storage


class UserUpdate(BaseModel):
    username: Optional[str] = None
    role: Optional[UserRole] = None
    password: Optional[str] = None


class UserOut(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int