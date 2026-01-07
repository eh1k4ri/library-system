from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.errors import ReservationNotFound
from app.db.session import get_session
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.services.reservation_service import ReservationService

router = APIRouter()
service = ReservationService()


@router.post(
    "/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED
)
def create_reservation(
    reservation: ReservationCreate,
    session: Session = Depends(get_session),
):
    return service.create(session, reservation)


@router.get("/", response_model=List[ReservationResponse])
def get_reservations(
    user_key: Optional[str] = None,
    book_key: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    return service.get_all(
        session,
        skip=skip,
        limit=limit,
        user_key=user_key,
        book_key=book_key,
        status=status,
    )


@router.get("/{reservation_key}", response_model=ReservationResponse)
def get_reservation(reservation_key: UUID, session: Session = Depends(get_session)):
    reservation = service.get_by_key(session, reservation_key)
    if reservation is None:
        raise ReservationNotFound()
    return reservation


@router.delete("/{reservation_key}", response_model=ReservationResponse)
def cancel_reservation(
    reservation_key: UUID,
    session: Session = Depends(get_session),
):
    return service.cancel_reservation(session, reservation_key)


@router.post("/{reservation_key}/complete", response_model=ReservationResponse)
def complete_reservation(
    reservation_key: UUID,
    session: Session = Depends(get_session),
):
    return service.complete_reservation(session, reservation_key)
