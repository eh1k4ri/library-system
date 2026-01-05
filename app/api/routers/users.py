from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.loan import LoanResponse
from app.services.user_service import UserService

router = APIRouter()
service = UserService()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return service.create(db=db, user=user)


@router.get("/", response_model=List[UserResponse])
def get_users(page: int = 1, per_page: int = 100, db: Session = Depends(get_db)):
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if per_page < 1:
        raise HTTPException(status_code=400, detail="per_page must be >= 1")
    return service.get_all(db, page, per_page)


@router.get("/{user_key}", response_model=UserResponse)
def get_user(user_key: UUID, db: Session = Depends(get_db)):
    user = service.get_by_key(db, user_key)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/{user_key}/loans", response_model=List[LoanResponse])
def get_user_loans(
    user_key: UUID, page: int = 1, per_page: int = 100, db: Session = Depends(get_db)
):
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if per_page < 1:
        raise HTTPException(status_code=400, detail="per_page must be >= 1")
    loans = service.get_user_loans(db, user_key, page, per_page)
    if loans is None:
        raise HTTPException(status_code=404, detail="User not found")
    return loans
