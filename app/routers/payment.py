from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.payment import PaymentCreate, PaymentUpdate, PaymentOut
from app.repositories import payment as payment_repo

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("", response_model=PaymentOut, status_code=status.HTTP_201_CREATED)
def create_payment(payload: PaymentCreate, db: Session = Depends(get_db)):
    return payment_repo.create(db, payload)


@router.get("", response_model=List[PaymentOut])
def list_payments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return payment_repo.get_all(db, skip, limit)


@router.get("/{payment_id}", response_model=PaymentOut)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    obj = payment_repo.get(db, payment_id)
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    return obj


@router.put("/{payment_id}", response_model=PaymentOut)
def update_payment(payment_id: int, payload: PaymentUpdate, db: Session = Depends(get_db)):
    obj = payment_repo.update(db, payment_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="Payment not found")
    return obj


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment(payment_id: int, db: Session = Depends(get_db)):
    if not payment_repo.delete(db, payment_id):
        raise HTTPException(status_code=404, detail="Payment not found")