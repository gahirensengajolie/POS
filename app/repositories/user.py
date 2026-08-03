from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create(db: Session, data: UserCreate) -> User:
    obj = User(
        username=data.username,
        role=data.role,
        password_hash=pwd_context.hash(data.password),
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()


def get_by_username(db: Session, username: str) -> Optional[User]:
    return db.query(User).filter(User.username == username).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    return db.query(User).offset(skip).limit(limit).all()


def update(db: Session, user_id: int, data: UserUpdate) -> Optional[User]:
    obj = get(db, user_id)
    if not obj:
        return None
    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data:
        obj.password_hash = pwd_context.hash(update_data.pop("password"))
    for field, value in update_data.items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, user_id: int) -> bool:
    obj = get(db, user_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True