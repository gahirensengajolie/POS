from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.payment import Payment
from app.schemas.payment import PaymentCreate, PaymentUpdate


def create(db: Session, data: PaymentCreate) -> Payment:
    obj = Payment(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, payment_id: int) -> Optional[Payment]:
    return db.query(Payment).filter(Payment.id == payment_id).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Payment]:
    return db.query(Payment).offset(skip).limit(limit).all()


def update(db: Session, payment_id: int, data: PaymentUpdate) -> Optional[Payment]:
    obj = get(db, payment_id)
    if not obj:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, payment_id: int) -> bool:
    obj = get(db, payment_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True