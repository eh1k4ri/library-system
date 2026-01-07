from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.reservation import Reservation
from app.models.reservation_status import ReservationStatus
from app.models.user import User
from app.models.book import Book
from app.models.book_status import BookStatus
from app.schemas.reservation import ReservationCreate
from app.core.constants import CACHE_ENTITY_TTL, RESERVATION_EXPIRY_DAYS
from app.core.errors import (
    ReservationNotFound,
    CannotReserveAvailableBook,
    DuplicateActiveReservation,
    ReservationAlreadyCancelled,
    CannotCancelCompletedReservation,
    CannotCompleteInactiveReservation,
    UserNotFound,
    BookNotFound,
)
from app.utils.uuid import validate_uuid
from app.utils.cache import get_cache, set_cache


class ReservationService:

    def create(self, session: Session, reservation_data: ReservationCreate):
        user = (
            session.query(User)
            .filter(User.user_key == reservation_data.user_key)
            .first()
        )
        if not user:
            raise UserNotFound()

        book = (
            session.query(Book)
            .filter(Book.book_key == reservation_data.book_key)
            .first()
        )
        if not book:
            raise BookNotFound()

        available_status = (
            session.query(BookStatus)
            .filter(BookStatus.enumerator == "available")
            .first()
        )
        if book.status_id == available_status.id:
            raise CannotReserveAvailableBook()

        active_status = (
            session.query(ReservationStatus)
            .filter(ReservationStatus.enumerator == "active")
            .first()
        )

        existing_reservation = (
            session.query(Reservation)
            .filter(
                and_(
                    Reservation.user_id == user.id,
                    Reservation.book_id == book.id,
                    Reservation.status_id == active_status.id,
                )
            )
            .first()
        )
        if existing_reservation:
            raise DuplicateActiveReservation()

        expires_at = datetime.now() + timedelta(days=RESERVATION_EXPIRY_DAYS)
        new_reservation = Reservation(
            user_id=user.id,
            book_id=book.id,
            status_id=active_status.id,
            expires_at=expires_at,
        )
        session.add(new_reservation)
        session.commit()
        session.refresh(new_reservation)

        full_reservation = self._get_with_relations(
            session, new_reservation.reservation_key
        )

        return full_reservation

    def get_all(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        user_key: str = None,
        book_key: str = None,
        status: str = None,
    ):
        query = session.query(Reservation).options(
            joinedload(Reservation.user),
            joinedload(Reservation.book),
            joinedload(Reservation.status),
        )

        if user_key:
            user_key = validate_uuid(user_key)
            if user_key:
                query = query.join(User).filter(User.user_key == user_key)

        if book_key:
            book_key = validate_uuid(book_key)
            if book_key:
                query = query.join(Book).filter(Book.book_key == book_key)

        if status:
            query = query.join(Reservation.status).filter(
                ReservationStatus.enumerator == status.lower()
            )
        reservations = (
            query.order_by(Reservation.reserved_at).offset(skip).limit(limit).all()
        )
        return reservations

    def get_by_key(self, session: Session, reservation_key: str):
        reservation_key = validate_uuid(reservation_key)
        if not reservation_key:
            return None

        cache_key = f"reservation:{reservation_key}:details"
        cached_reservation = get_cache(cache_key)
        if cached_reservation:
            return cached_reservation

        reservation = self._get_with_relations(session, reservation_key)

        if reservation:
            set_cache(cache_key, reservation, ttl_seconds=CACHE_ENTITY_TTL)

        return reservation

    def cancel_reservation(self, session: Session, reservation_key: str):
        reservation_key = validate_uuid(reservation_key)
        if not reservation_key:
            raise ReservationNotFound()

        reservation = self._get_with_relations(session, reservation_key)

        if not reservation:
            raise ReservationNotFound()

        cancelled_status = (
            session.query(ReservationStatus)
            .filter(ReservationStatus.enumerator == "cancelled")
            .first()
        )
        completed_status = (
            session.query(ReservationStatus)
            .filter(ReservationStatus.enumerator == "completed")
            .first()
        )

        if reservation.status_id == cancelled_status.id:
            raise ReservationAlreadyCancelled()
        if reservation.status_id == completed_status.id:
            raise CannotCancelCompletedReservation()

        reservation.status_id = cancelled_status.id
        session.commit()

        cache_key = f"reservation:{reservation_key}:details"
        updated = self._get_with_relations(session, reservation_key)
        set_cache(cache_key, updated, ttl_seconds=CACHE_ENTITY_TTL)

        return updated

    def complete_reservation(self, session: Session, reservation_key: str):
        reservation_key = validate_uuid(reservation_key)
        if not reservation_key:
            raise ReservationNotFound()

        reservation = self._get_with_relations(session, reservation_key)

        if not reservation:
            raise ReservationNotFound()

        active_status = (
            session.query(ReservationStatus)
            .filter(ReservationStatus.enumerator == "active")
            .first()
        )
        if reservation.status_id != active_status.id:
            raise CannotCompleteInactiveReservation()

        completed_status = (
            session.query(ReservationStatus)
            .filter(ReservationStatus.enumerator == "completed")
            .first()
        )
        reservation.status_id = completed_status.id
        reservation.completed_at = datetime.now()

        session.commit()

        cache_key = f"reservation:{reservation_key}:details"
        updated = self._get_with_relations(session, reservation_key)
        set_cache(cache_key, updated, ttl_seconds=CACHE_ENTITY_TTL)

        return updated

    def _get_with_relations(self, session: Session, reservation_key):
        return (
            session.query(Reservation)
            .options(
                joinedload(Reservation.user),
                joinedload(Reservation.book),
                joinedload(Reservation.status),
            )
            .filter(Reservation.reservation_key == reservation_key)
            .first()
        )
