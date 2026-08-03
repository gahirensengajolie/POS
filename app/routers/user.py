from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.user import UserCreate, UserUpdate, UserOut
from app.repositories import user as user_repo

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    if user_repo.get_by_username(db, payload.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    return user_repo.create(db, payload)


@router.get("", response_model=List[UserOut])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return user_repo.get_all(db, skip, limit)


@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    obj = user_repo.get(db, user_id)
    if not obj:
        raise HTTPException(status_code=404, detail="User not found")
    return obj


@router.put("/{user_id}", response_model=UserOut)
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    obj = user_repo.update(db, user_id, payload)
    if not obj:
        raise HTTPException(status_code=404, detail="User not found")
    return obj


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    if not user_repo.delete(db, user_id):
        raise HTTPException(status_code=404, detail="User not found")