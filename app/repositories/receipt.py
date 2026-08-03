from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.receipt import Receipt
from app.schemas.receipt import ReceiptCreate, ReceiptUpdate


def create(db: Session, data: ReceiptCreate) -> Receipt:
    obj = Receipt(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, receipt_id: int) -> Optional[Receipt]:
    return db.query(Receipt).filter(Receipt.id == receipt_id).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Receipt]:
    return db.query(Receipt).offset(skip).limit(limit).all()


def update(db: Session, receipt_id: int, data: ReceiptUpdate) -> Optional[Receipt]:
    obj = get(db, receipt_id)
    if not obj:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, receipt_id: int) -> bool:
    obj = get(db, receipt_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True