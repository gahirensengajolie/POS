from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.sale_item import SaleItemCreate, SaleItemUpdate, SaleItemOut
from app.repositories import sale_item as sale_item_repo

router = APIRouter(prefix="/sale-items", tags=["Sale Items"])


@router.post("", response_model=SaleItemOut, status_code=status.HTTP_201_CREATED)
def create_sale_item(payload: SaleItemCreate, db: Session = Depends(get_db)):
    return sale_item_repo.create(db, payload)


@router.get("", response_model=List[SaleItemOut])
def list_sale_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return sale_item_repo.get_all(db, skip, limit)


@router.get("/{sale_item_id}", response_model=SaleItemOut)
def get_sale_item(sale_item_id: int, db: Session = Depends(get_db)):
    obj = sale_item_repo.get(db, sale_item_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Sale item not found")
    return obj


@router.get("/by-sale/{sale_id}", response_model=List[SaleItemOut])
def get_items_by_sale(sale_id: int, db: Session = Depends(get_db)):
    return sale_item_repo.get_by_sale(db, sale_id)


@router.put("/{sale_item_id}", response_model=SaleItemOut)
def update_sale_item(sale_item_id: int, payload: SaleItemUpdate, db: Session = Depends(get_db)):
    obj = sale_item_repo.update(db, sale_item_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Sale item not found")
    return obj


@router.delete("/{sale_item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale_item(sale_item_id: int, db: Session = Depends(get_db)):
    if not sale_item_repo.delete(db, sale_item_id):
        raise HTTPException(status_code=404, detail="Sale item not found")