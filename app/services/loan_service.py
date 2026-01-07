from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session, joinedload
from app.models.loan import Loan
from app.models.book import Book
from app.models.user import User
from app.models.book_status import BookStatus
from app.models.loan_status import LoanStatus
from app.models.loan_event import LoanEvent
from app.schemas.loan import LoanCreate, LoanReturnRequest
from app.services.notification_service import notification_service
from app.core.constants import (
    LOAN_DEFAULT_DAYS,
    LOAN_FINE_PER_DAY,
    LOAN_MAX_ACTIVE_LOANS,
    LOAN_RENEWAL_EXTENSION_DAYS,
    CACHE_ENTITY_TTL,
)
from app.core.errors import (
    UserNotFound,
    UserNotActive,
    MaxActiveLoansReached,
    BookNotFound,
    BookNotAvailable,
    ActiveLoanNotFound,
    LoanNotFound,
    CannotRenewInactiveLoan,
    CannotRenewOverdueLoan,
)
from app.utils.uuid import validate_uuid
from app.utils.cache import get_cache, set_cache, clear_cache


class LoanService:
    def create(self, session: Session, loan_data: LoanCreate):
        user = (
            session.query(User)
            .options(joinedload(User.status))
            .filter(User.user_key == loan_data.user_key)
            .first()
        )
        if not user:
            raise UserNotFound()
        if user.status.enumerator != "active":
            raise UserNotActive()

        active_loan_status = (
            session.query(LoanStatus).filter(LoanStatus.enumerator == "active").first()
        )

        active_loans_count = (
            session.query(Loan)
            .filter(Loan.user_id == user.id, Loan.status_id == active_loan_status.id)
            .count()
        )
        if active_loans_count >= LOAN_MAX_ACTIVE_LOANS:
            raise MaxActiveLoansReached()

        book = (
            session.query(Book)
            .filter(Book.book_key == loan_data.book_key)
            .with_for_update()
            .first()
        )

        if not book:
            raise BookNotFound()
        if book.status.enumerator != "available":
            raise BookNotAvailable()

        try:
            loaned_status = (
                session.query(BookStatus)
                .filter(BookStatus.enumerator == "loaned")
                .first()
            )

            book.status_id = loaned_status.id

            now = datetime.now(timezone.utc)
            due_date = now + timedelta(days=LOAN_DEFAULT_DAYS)

            new_loan = Loan(
                user_id=user.id,
                book_id=book.id,
                status_id=active_loan_status.id,
                start_date=now,
                due_date=due_date,
                fine_amount=0.0,
            )
            session.add(new_loan)
            session.flush()

            event = LoanEvent(
                loan_id=new_loan.id,
                old_status_id=None,
                new_status_id=active_loan_status.id,
                created_at=now,
            )
            session.add(event)

            session.commit()
            session.refresh(new_loan)

            clear_cache(f"book:{book.book_key}:details")

            try:
                notification_service.notify_due_date(
                    user_email=user.email,
                    loan_key=str(new_loan.loan_key),
                    book_title=book.title,
                    due_date=due_date,
                )
            except Exception:
                pass
            return new_loan

        except Exception as exc:
            session.rollback()
            raise exc

    def get_all(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        status: str = None,
        overdue: bool = False,
    ):
        query = session.query(Loan).options(
            joinedload(Loan.user), joinedload(Loan.book), joinedload(Loan.status)
        )

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

    def get_by_key(self, session: Session, loan_key: str):
        loan_key = validate_uuid(loan_key)
        if not loan_key:
            return None

        cache_key = f"loan:{loan_key}:details"
        cached_loan = get_cache(cache_key)
        if cached_loan:
            return cached_loan

        loan = (
            session.query(Loan)
            .options(
                joinedload(Loan.user), joinedload(Loan.book), joinedload(Loan.status)
            )
            .filter(Loan.loan_key == loan_key)
            .first()
        )

        if loan:
            set_cache(cache_key, loan, ttl_seconds=CACHE_ENTITY_TTL)

        return loan

    def return_book(self, session: Session, return_data: LoanReturnRequest):
        book = session.query(Book).filter(Book.book_key == return_data.book_key).first()
        if not book:
            raise BookNotFound()

        active_status = (
            session.query(LoanStatus).filter(LoanStatus.enumerator == "active").first()
        )
        returned_status = (
            session.query(LoanStatus)
            .filter(LoanStatus.enumerator == "returned")
            .first()
        )
        available_book_status = (
            session.query(BookStatus)
            .filter(BookStatus.enumerator == "available")
            .first()
        )

        loan = (
            session.query(Loan)
            .filter(Loan.book_id == book.id, Loan.status_id == active_status.id)
            .first()
        )

        if not loan:
            raise ActiveLoanNotFound()

        try:
            now = datetime.now(timezone.utc)
            fine = 0.0

            if loan.due_date:
                due_date_aware = (
                    loan.due_date
                    if loan.due_date.tzinfo
                    else loan.due_date.replace(tzinfo=timezone.utc)
                )

                if now > due_date_aware:
                    days_late = (now - due_date_aware).days
                    if days_late > 0:
                        fine = days_late * LOAN_FINE_PER_DAY

            loan.return_date = now
            loan.status_id = returned_status.id
            loan.fine_amount = fine

            book.status_id = available_book_status.id

            event = LoanEvent(
                loan_id=loan.id,
                old_status_id=active_status.id,
                new_status_id=returned_status.id,
                created_at=now,
            )
            session.add(event)

            session.commit()
            session.refresh(loan)

            clear_cache(f"book:{return_data.book_key}:details")

            return loan

        except Exception as exc:
            session.rollback()
            raise exc

    def renew_loan(self, session: Session, loan_key: str):
        loan_key = validate_uuid(loan_key)
        if not loan_key:
            raise LoanNotFound()

        loan = (
            session.query(Loan)
            .options(
                joinedload(Loan.user),
                joinedload(Loan.book),
                joinedload(Loan.status),
                joinedload(Loan.events).joinedload(LoanEvent.new_status),
                joinedload(Loan.events).joinedload(LoanEvent.old_status),
            )
            .filter(Loan.loan_key == loan_key)
            .first()
        )

        if not loan:
            raise LoanNotFound()

        active_status = (
            session.query(LoanStatus).filter(LoanStatus.enumerator == "active").first()
        )

        if loan.status_id != active_status.id:
            raise CannotRenewInactiveLoan()

        now = datetime.now(timezone.utc)
        due_date = loan.due_date
        if due_date and due_date.tzinfo is None:
            due_date = due_date.replace(tzinfo=timezone.utc)

        if due_date and due_date <= now:
            raise CannotRenewOverdueLoan()

        extension = timedelta(days=LOAN_RENEWAL_EXTENSION_DAYS)
        loan.due_date = (due_date or now) + extension

        event = LoanEvent(
            loan_id=loan.id,
            old_status_id=active_status.id,
            new_status_id=active_status.id,
            created_at=now,
        )
        session.add(event)

        session.commit()
        session.refresh(loan)

        cache_key = f"loan:{loan_key}:details"
        set_cache(cache_key, loan, ttl_seconds=60)

        return loan
