from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.sale import SaleCreate, SaleUpdate, SaleOut
from app.repositories import sale as sale_repo

router = APIRouter(prefix="/sales", tags=["Sales"])


@router.post("", response_model=SaleOut, status_code=status.HTTP_201_CREATED)
def create_sale(payload: SaleCreate, db: Session = Depends(get_db)):
    return sale_repo.create(db, payload)


@router.get("", response_model=List[SaleOut])
def list_sales(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return sale_repo.get_all(db, skip, limit)


@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db)):
    obj = sale_repo.get(db, sale_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Sale not found")
    return obj


@router.put("/{sale_id}", response_model=SaleOut)
def update_sale(sale_id: int, payload: SaleUpdate, db: Session = Depends(get_db)):
    obj = sale_repo.update(db, sale_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Sale not found")
    return obj


@router.delete("/{sale_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_sale(sale_id: int, db: Session = Depends(get_db)):
    if not sale_repo.delete(db, sale_id):
        raise HTTPException(status_code=404, detail="Sale not found")