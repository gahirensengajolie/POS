from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.supplier import SupplierCreate, SupplierUpdate, SupplierOut
from app.repositories import supplier as supplier_repo

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.post("", response_model=SupplierOut, status_code=status.HTTP_201_CREATED)
def create_supplier(payload: SupplierCreate, db: Session = Depends(get_db)):
    return supplier_repo.create(db, payload)


@router.get("", response_model=List[SupplierOut])
def list_suppliers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return supplier_repo.get_all(db, skip, limit)


@router.get("/{supplier_id}", response_model=SupplierOut)
def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    obj = supplier_repo.get(db, supplier_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return obj


@router.put("/{supplier_id}", response_model=SupplierOut)
def update_supplier(supplier_id: int, payload: SupplierUpdate, db: Session = Depends(get_db)):
    obj = supplier_repo.update(db, supplier_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return obj


@router.delete("/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_supplier(supplier_id: int, db: Session = Depends(get_db)):
    if not supplier_repo.delete(db, supplier_id):
        raise HTTPException(status_code=404, detail="Supplier not found")