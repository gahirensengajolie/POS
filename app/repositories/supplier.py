from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.supplier import Supplier
from app.schemas.supplier import SupplierCreate, SupplierUpdate


def create(db: Session, data: SupplierCreate) -> Supplier:
    obj = Supplier(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, supplier_id: int) -> Optional[Supplier]:
    return db.query(Supplier).filter(Supplier.id == supplier_id).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Supplier]:
    return db.query(Supplier).offset(skip).limit(limit).all()


def update(db: Session, supplier_id: int, data: SupplierUpdate) -> Optional[Supplier]:
    obj = get(db, supplier_id)
    if not obj:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, supplier_id: int) -> bool:
    obj = get(db, supplier_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True