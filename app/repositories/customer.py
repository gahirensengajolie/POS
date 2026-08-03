from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


def create(db: Session, data: CustomerCreate) -> Customer:
    obj = Customer(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, customer_id: int) -> Optional[Customer]:
    return db.query(Customer).filter(Customer.id == customer_id).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Customer]:
    return db.query(Customer).offset(skip).limit(limit).all()


def update(db: Session, customer_id: int, data: CustomerUpdate) -> Optional[Customer]:
    obj = get(db, customer_id)
    if not obj:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, customer_id: int) -> bool:
    obj = get(db, customer_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True