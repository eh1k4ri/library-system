import uuid
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.loan import Loan
from app.models.book import Book
from app.models.user import User
from app.models.book_status import BookStatus
from app.models.loan_status import LoanStatus
from app.models.loan_event import LoanEvent
from app.schemas.loan import LoanCreate, LoanReturnRequest


class LoanService:
    def get_loans(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Loan).offset(skip).limit(limit).all()

    def get_loan_by_key(self, db: Session, loan_key: str):
        try:
            loan_key = uuid.UUID(str(loan_key))
        except Exception:
            return None
        return db.query(Loan).filter(Loan.loan_key == loan_key).first()

    def create_loan(self, db: Session, loan_data: LoanCreate):
        user = db.query(User).filter(User.user_key == loan_data.user_key).first()
        if not user:
            raise HTTPException(404, "User not found")
        if user.status.enumerator != "active":
            raise HTTPException(400, "User is not active")

        active_loan_status = (
            db.query(LoanStatus).filter(LoanStatus.enumerator == "active").first()
        )

        active_loans_count = (
            db.query(Loan)
            .filter(Loan.user_id == user.id, Loan.status_id == active_loan_status.id)
            .count()
        )
        if active_loans_count >= 3:
            raise HTTPException(400, "User has reached maximum of 3 active loans")

        book = db.query(Book).filter(Book.book_key == loan_data.book_key).first()
        if not book:
            raise HTTPException(404, "Book not found")
        if book.status.enumerator != "available":
            raise HTTPException(400, "Book is not available")

        try:
            loaned_status = (
                db.query(BookStatus).filter(BookStatus.enumerator == "loaned").first()
            )

            book.status_id = loaned_status.id
            now = datetime.now(timezone.utc)
            due_date = now + timedelta(days=loan_data.days)

            new_loan = Loan(
                user_id=user.id,
                book_id=book.id,
                status_id=active_loan_status.id,
                start_date=now,
                due_date=due_date,
                fine_amount=0.0,
            )
            db.add(new_loan)
            db.flush()

            event = LoanEvent(
                loan_id=new_loan.id,
                old_status_id=None,
                new_status_id=active_loan_status.id,
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
            raise HTTPException(404, "Book not found")

        active_status = (
            db.query(LoanStatus).filter(LoanStatus.enumerator == "active").first()
        )
        loan = (
            db.query(Loan)
            .filter(Loan.book_id == book.id, Loan.status_id == active_status.id)
            .first()
        )

        if not loan:
            raise HTTPException(404, "No active loan found for this book")

        try:
            now = datetime.now(timezone.utc)

            fine = 0.0

            due_date = loan.due_date
            if due_date is not None and due_date.tzinfo is None:
                due_date = due_date.replace(tzinfo=timezone.utc)

            if due_date is not None and now > due_date:
                days_late = (now - due_date).days + 1
                fine = days_late * 2.0

            returned_status = (
                db.query(LoanStatus).filter(LoanStatus.enumerator == "returned").first()
            )
            available_book_status = (
                db.query(BookStatus)
                .filter(BookStatus.enumerator == "available")
                .first()
            )

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
            db.add(event)

            db.commit()
            db.refresh(loan)
            return loan
        except Exception as e:
            db.rollback()
            raise e
