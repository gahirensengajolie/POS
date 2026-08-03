from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.sale import Sale
from app.schemas.sale import SaleCreate, SaleUpdate


def create(db: Session, data: SaleCreate) -> Sale:
    obj = Sale(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, sale_id: int) -> Optional[Sale]:
    return db.query(Sale).filter(Sale.id == sale_id).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[Sale]:
    return db.query(Sale).offset(skip).limit(limit).all()


def update(db: Session, sale_id: int, data: SaleUpdate) -> Optional[Sale]:
    obj = get(db, sale_id)
    if not obj:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, sale_id: int) -> bool:
    obj = get(db, sale_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True