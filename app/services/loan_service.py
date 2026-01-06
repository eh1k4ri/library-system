from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models.loan import Loan
from app.models.book import Book
from app.models.user import User
from app.models.book_status import BookStatus
from app.models.loan_status import LoanStatus
from app.models.loan_event import LoanEvent
from app.schemas.loan import LoanCreate, LoanReturnRequest
from app.core.errors import (
    UserNotFound,
    UserNotActive,
    MaxActiveLoansReached,
    BookNotFound,
    BookNotAvailable,
    ActiveLoanNotFound,
)
from app.utils.uuid import validate_uuid
from app.utils.cache import get_cache, set_cache


class LoanService:
    def get_loans(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Loan).offset(skip).limit(limit).all()

    def get_loans_filtered(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        status: str | None = None,
        overdue: bool = False,
    ):
        query = db.query(Loan)

        if status:
            query = query.join(Loan.status).filter(LoanStatus.enumerator == status)

        if overdue:
            now = datetime.now(timezone.utc)
            query = (
                query.join(Loan.status)
                .filter(LoanStatus.enumerator == "active")
                .filter(Loan.due_date < now)
            )

        return query.offset(skip).limit(limit).all()

    def get_loan_by_key(self, db: Session, loan_key: str):
        loan_key = validate_uuid(loan_key)
        if not loan_key:
            return None
        return db.query(Loan).filter(Loan.loan_key == loan_key).first()

    def create_loan(self, db: Session, loan_data: LoanCreate):
        user = db.query(User).filter(User.user_key == loan_data.user_key).first()
        if not user:
            raise UserNotFound()
        if user.status.enumerator != "active":
            raise UserNotActive()

        loan_active_key = "status:loan:active:id"
        active_loan_status_id = get_cache(loan_active_key)
        if active_loan_status_id is None:
            active_loan_status = (
                db.query(LoanStatus).filter(LoanStatus.enumerator == "active").first()
            )
            active_loan_status_id = (
                active_loan_status.id if active_loan_status else None
            )
            if active_loan_status_id is not None:
                set_cache(loan_active_key, active_loan_status_id, ttl_seconds=300)
        if active_loan_status_id is None:
            raise RuntimeError("Loan status 'active' not configured")

        active_loans_count = (
            db.query(Loan)
            .filter(Loan.user_id == user.id, Loan.status_id == active_loan_status_id)
            .count()
        )
        if active_loans_count >= 3:
            raise MaxActiveLoansReached()

        book = db.query(Book).filter(Book.book_key == loan_data.book_key).first()
        if not book:
            raise BookNotFound()
        if book.status.enumerator != "available":
            raise BookNotAvailable()

        try:
            book_loaned_key = "status:book:loaned:id"
            loaned_status_id = get_cache(book_loaned_key)
            if loaned_status_id is None:
                loaned_status = (
                    db.query(BookStatus)
                    .filter(BookStatus.enumerator == "loaned")
                    .first()
                )
                loaned_status_id = loaned_status.id if loaned_status else None
                if loaned_status_id is not None:
                    set_cache(book_loaned_key, loaned_status_id, ttl_seconds=300)
            if loaned_status_id is None:
                raise RuntimeError("Book status 'loaned' not configured")

            book.status_id = loaned_status_id
            now = datetime.now(timezone.utc)
            due_date = now + timedelta(days=14)

            new_loan = Loan(
                user_id=user.id,
                book_id=book.id,
                status_id=active_loan_status_id,
                start_date=now,
                due_date=due_date,
                fine_amount=0.0,
            )
            db.add(new_loan)
            db.flush()

            event = LoanEvent(
                loan_id=new_loan.id,
                old_status_id=None,
                new_status_id=active_loan_status_id,
                created_at=now,
            )
            db.add(event)

            db.commit()
            db.refresh(new_loan)
            return new_loan

        except Exception as e:
            db.rollback()
            raise e

    def return_book(self, db: Session, return_data: LoanReturnRequest):
        book = db.query(Book).filter(Book.book_key == return_data.book_key).first()
        if not book:
            raise BookNotFound()

        loan_active_key = "status:loan:active:id"
        active_status_id = get_cache(loan_active_key)
        if active_status_id is None:
            active_status = (
                db.query(LoanStatus).filter(LoanStatus.enumerator == "active").first()
            )
            active_status_id = active_status.id if active_status else None
            if active_status_id is not None:
                set_cache(loan_active_key, active_status_id, ttl_seconds=300)
        if active_status_id is None:
            raise RuntimeError("Loan status 'active' not configured")
        loan = (
            db.query(Loan)
            .filter(Loan.book_id == book.id, Loan.status_id == active_status_id)
            .first()
        )

        if not loan:
            raise ActiveLoanNotFound()

        try:
            now = datetime.now(timezone.utc)
            fine = 0.0
            due_date = loan.due_date

            if due_date is not None and due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)

            if due_date is not None and now > due_date:
                days_late = (now - due_date).days + 1
                fine = days_late * 2.0

            loan_returned_key = "status:loan:returned:id"
            returned_status_id = get_cache(loan_returned_key)
            if returned_status_id is None:
                returned_status = (
                    db.query(LoanStatus)
                    .filter(LoanStatus.enumerator == "returned")
                    .first()
                )
                returned_status_id = returned_status.id if returned_status else None
                if returned_status_id is not None:
                    set_cache(loan_returned_key, returned_status_id, ttl_seconds=300)
            if returned_status_id is None:
                raise RuntimeError("Loan status 'returned' not configured")

            book_available_key = "status:book:available:id"
            available_book_status_id = get_cache(book_available_key)
            if available_book_status_id is None:
                available_book_status = (
                    db.query(BookStatus)
                    .filter(BookStatus.enumerator == "available")
                    .first()
                )
                available_book_status_id = (
                    available_book_status.id if available_book_status else None
                )
                if available_book_status_id is not None:
                    set_cache(
                        book_available_key, available_book_status_id, ttl_seconds=300
                    )
            if available_book_status_id is None:
                raise RuntimeError("Book status 'available' not configured")

            loan.return_date = now
            loan.status_id = returned_status_id
            loan.fine_amount = fine
            book.status_id = available_book_status_id
            event = LoanEvent(
                loan_id=loan.id,
                old_status_id=active_status_id,
                new_status_id=returned_status_id,
                created_at=now,
            )
            db.add(event)

            db.commit()
            db.refresh(loan)
            return loan
        except Exception as e:
            db.rollback()
            raise e
