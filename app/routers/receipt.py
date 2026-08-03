from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.receipt import ReceiptCreate, ReceiptUpdate, ReceiptOut
from app.repositories import receipt as receipt_repo

router = APIRouter(prefix="/receipts", tags=["Receipts"])


@router.post("", response_model=ReceiptOut, status_code=status.HTTP_201_CREATED)
def create_receipt(payload: ReceiptCreate, db: Session = Depends(get_db)):
    return receipt_repo.create(db, payload)


@router.get("", response_model=List[ReceiptOut])
def list_receipts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return receipt_repo.get_all(db, skip, limit)


@router.get("/{receipt_id}", response_model=ReceiptOut)
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    obj = receipt_repo.get(db, receipt_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return obj


@router.put("/{receipt_id}", response_model=ReceiptOut)
def update_receipt(receipt_id: int, payload: ReceiptUpdate, db: Session = Depends(get_db)):
    obj = receipt_repo.update(db, receipt_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Receipt not found")
    return obj


@router.delete("/{receipt_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_receipt(receipt_id: int, db: Session = Depends(get_db)):
    if not receipt_repo.delete(db, receipt_id):
        raise HTTPException(status_code=404, detail="Receipt not found")