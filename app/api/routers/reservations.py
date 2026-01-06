from typing import List, Optional
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.db.session import get_db
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.services.reservation_service import ReservationService
from app.core.errors import ReservationNotFound

router = APIRouter()
service = ReservationService()


@router.post(
    "/", response_model=ReservationResponse, status_code=status.HTTP_201_CREATED
)
def create_reservation(
    reservation: ReservationCreate,
    db: Session = Depends(get_db),
):
    return service.create_reservation(db, reservation)


@router.get("/", response_model=List[ReservationResponse])
def read_reservations(
    user_key: Optional[str] = None,
    book_key: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    return service.get_reservations(
        db,
        skip=skip,
        limit=limit,
        user_key=user_key,
        book_key=book_key,
        status=status,
    )


@router.get("/{reservation_key}", response_model=ReservationResponse)
def read_reservation(reservation_key: UUID, db: Session = Depends(get_db)):
    reservation = service.get_reservation_by_key(db, reservation_key)
    if reservation is None:
        raise ReservationNotFound()
    return reservation


@router.delete("/{reservation_key}", response_model=ReservationResponse)
def cancel_reservation(
    reservation_key: UUID,
    db: Session = Depends(get_db),
):
    return service.cancel_reservation(db, reservation_key)


@router.post("/{reservation_key}/complete", response_model=ReservationResponse)
def complete_reservation(
    reservation_key: UUID,
    db: Session = Depends(get_db),
):
    return service.complete_reservation(db, reservation_key)
