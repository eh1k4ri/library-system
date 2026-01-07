from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.db.session import get_session
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.loan import LoanResponse
from app.services.user_service import UserService
from app.api.deps import PaginationParams
from app.core.errors import UserNotFound, InvalidStatus

router = APIRouter()
service = UserService()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    return service.create(session=session, user=user)


@router.patch("/{user_key}", response_model=UserResponse)
def update_user(
    user_key: UUID, payload: UserUpdate, session: Session = Depends(get_session)
):
    updated = service.update(session=session, user_key=str(user_key), data=payload)
    if not updated:
        raise UserNotFound()
    return updated


@router.post("/{user_key}/status", response_model=UserResponse)
def change_user_status(
    user_key: UUID, status_enum: str, session: Session = Depends(get_session)
):
    updated = service.set_status(
        session=session, user_key=str(user_key), status_enum=status_enum
    )
    if not updated:
        raise InvalidStatus()
    return updated


@router.get("/", response_model=List[UserResponse])
def get_users(
    pagination: PaginationParams = Depends(), session: Session = Depends(get_session)
):
    return service.get_all(session, skip=pagination.skip, limit=pagination.per_page)


@router.get("/{user_key}", response_model=UserResponse)
def get_user(user_key: UUID, session: Session = Depends(get_session)):
    user = service.get_by_key(session, user_key)
    if user is None:
        raise UserNotFound()
    return user


@router.get("/{user_key}/loans", response_model=List[LoanResponse])
def get_user_loans(
    user_key: UUID,
    status: Optional[str] = None,
    pagination: PaginationParams = Depends(),
    session: Session = Depends(get_session),
):
    loans = service.get_user_loans(
        session,
        user_key,
        skip=pagination.skip,
        limit=pagination.per_page,
        status=status,
    )
    return loans
