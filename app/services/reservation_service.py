from datetime import datetime, timedelta
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from app.models.reservation import Reservation
from app.models.reservation_status import ReservationStatus
from app.models.user import User
from app.models.book import Book
from app.models.book_status import BookStatus
from app.schemas.reservation import ReservationCreate
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
    RESERVATION_EXPIRY_DAYS = 7

    def create_reservation(self, db: Session, reservation_data: ReservationCreate):
        user = db.query(User).filter(User.user_key == reservation_data.user_key).first()
        if not user:
            raise UserNotFound()

        book = db.query(Book).filter(Book.book_key == reservation_data.book_key).first()
        if not book:
            raise BookNotFound()

        available_status = (
            db.query(BookStatus).filter(BookStatus.enumerator == "available").first()
        )
        if book.status_id == available_status.id:
            raise CannotReserveAvailableBook()

        active_status = (
            db.query(ReservationStatus)
            .filter(ReservationStatus.enumerator == "active")
            .first()
        )

        existing_reservation = (
            db.query(Reservation)
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

        expires_at = datetime.now() + timedelta(days=self.RESERVATION_EXPIRY_DAYS)
        new_reservation = Reservation(
            user_id=user.id,
            book_id=book.id,
            status_id=active_status.id,
            expires_at=expires_at,
        )
        db.add(new_reservation)
        db.commit()
        db.refresh(new_reservation)

        full_reservation = self._get_with_relations(db, new_reservation.reservation_key)
        serialized = self._serialize(full_reservation)
        cache_key = f"reservation:{full_reservation.reservation_key}:details"
        set_cache(cache_key, serialized, ttl_seconds=60)

        return serialized

    def get_reservations(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        user_key: str | None = None,
        book_key: str | None = None,
        status: str | None = None,
    ):
        query = db.query(Reservation).options(
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
        return [self._serialize(r) for r in reservations]

    def get_reservation_by_key(self, db: Session, reservation_key: str):
        reservation_key = validate_uuid(reservation_key)
        if not reservation_key:
            return None

        cache_key = f"reservation:{reservation_key}:details"
        cached_reservation = get_cache(cache_key)
        if cached_reservation:
            return cached_reservation

        reservation = self._get_with_relations(db, reservation_key)

        if reservation:
            serialized = self._serialize(reservation)
            set_cache(cache_key, serialized, ttl_seconds=60)
            return serialized

        return None

    def cancel_reservation(self, db: Session, reservation_key: str):
        reservation_key = validate_uuid(reservation_key)
        if not reservation_key:
            raise ReservationNotFound()

        reservation = self._get_with_relations(db, reservation_key)

        if not reservation:
            raise ReservationNotFound()

        cancelled_status = (
            db.query(ReservationStatus)
            .filter(ReservationStatus.enumerator == "cancelled")
            .first()
        )
        completed_status = (
            db.query(ReservationStatus)
            .filter(ReservationStatus.enumerator == "completed")
            .first()
        )

        if reservation.status_id == cancelled_status.id:
            raise ReservationAlreadyCancelled()
        if reservation.status_id == completed_status.id:
            raise CannotCancelCompletedReservation()

        reservation.status_id = cancelled_status.id
        db.commit()
        cache_key = f"reservation:{reservation_key}:details"
        updated = self._get_with_relations(db, reservation_key)
        serialized = self._serialize(updated)
        set_cache(cache_key, serialized, ttl_seconds=60)

        return serialized

    def complete_reservation(self, db: Session, reservation_key: str):
        reservation_key = validate_uuid(reservation_key)
        if not reservation_key:
            raise ReservationNotFound()

        reservation = self._get_with_relations(db, reservation_key)

        if not reservation:
            raise ReservationNotFound()

        active_status = (
            db.query(ReservationStatus)
            .filter(ReservationStatus.enumerator == "active")
            .first()
        )
        if reservation.status_id != active_status.id:
            raise CannotCompleteInactiveReservation()

        completed_status = (
            db.query(ReservationStatus)
            .filter(ReservationStatus.enumerator == "completed")
            .first()
        )
        reservation.status_id = completed_status.id
        reservation.completed_at = datetime.now()
        db.commit()
        cache_key = f"reservation:{reservation_key}:details"
        updated = self._get_with_relations(db, reservation_key)
        serialized = self._serialize(updated)
        set_cache(cache_key, serialized, ttl_seconds=60)

        return serialized

    def _get_with_relations(self, db: Session, reservation_key):
        return (
            db.query(Reservation)
            .options(
                joinedload(Reservation.user),
                joinedload(Reservation.book),
                joinedload(Reservation.status),
            )
            .filter(Reservation.reservation_key == reservation_key)
            .first()
        )

    @staticmethod
    def _serialize(reservation: Reservation):
        return {
            "reservation_key": reservation.reservation_key,
            "reserved_at": reservation.reserved_at,
            "expires_at": reservation.expires_at,
            "completed_at": reservation.completed_at,
            "user_id": reservation.user_id,
            "user_key": reservation.user.user_key if reservation.user else None,
            "user_name": reservation.user.name if reservation.user else None,
            "book_id": reservation.book_id,
            "book_key": reservation.book.book_key if reservation.book else None,
            "book_title": reservation.book.title if reservation.book else None,
            "status_name": (
                reservation.status.enumerator if reservation.status else None
            ),
        }
