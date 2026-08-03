from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.sale_item import SaleItem
from app.schemas.sale_item import SaleItemCreate, SaleItemUpdate


def create(db: Session, data: SaleItemCreate) -> SaleItem:
    obj = SaleItem(**data.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


def get(db: Session, sale_item_id: int) -> Optional[SaleItem]:
    return db.query(SaleItem).filter(SaleItem.id == sale_item_id).first()


def get_all(db: Session, skip: int = 0, limit: int = 100) -> List[SaleItem]:
    return db.query(SaleItem).offset(skip).limit(limit).all()


def get_by_sale(db: Session, sale_id: int) -> List[SaleItem]:
    return db.query(SaleItem).filter(SaleItem.sale_id == sale_id).all()


def update(db: Session, sale_item_id: int, data: SaleItemUpdate) -> Optional[SaleItem]:
    obj = get(db, sale_item_id)
    if not obj:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    db.commit()
    db.refresh(obj)
    return obj


def delete(db: Session, sale_item_id: int) -> bool:
    obj = get(db, sale_item_id)
    if not obj:
        return False
    db.delete(obj)
    db.commit()
    return True