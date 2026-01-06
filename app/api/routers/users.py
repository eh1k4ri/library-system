from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse
from app.schemas.loan import LoanResponse
from app.services.user_service import UserService
from app.api.deps import PaginationParams
from app.core.errors import UserNotFound

router = APIRouter()
service = UserService()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return service.create(db=db, user=user)


@router.get("/", response_model=List[UserResponse])
def get_users(pagination: PaginationParams = Depends(), db: Session = Depends(get_db)):
    return service.get_all(db, skip=pagination.skip, limit=pagination.per_page)


@router.get("/{user_key}", response_model=UserResponse)
def get_user(user_key: UUID, db: Session = Depends(get_db)):
    user = service.get_by_key(db, user_key)
    if user is None:
        raise UserNotFound()
    return user


@router.get("/{user_key}/loans", response_model=List[LoanResponse])
def get_user_loans(
    user_key: UUID,
    pagination: PaginationParams = Depends(),
    db: Session = Depends(get_db),
):
    loans = service.get_user_loans(
        db, user_key, skip=pagination.skip, limit=pagination.per_page
    )
    return loans
