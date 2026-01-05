from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.book import Book
from app.models.book_status import BookStatus
from app.models.loan import Loan
from app.models.loan_status import LoanStatus
from app.schemas.book import BookCreate
import uuid


class BookService:
    def create(self, db: Session, book: BookCreate):
        available_status = (
            db.query(BookStatus).filter(BookStatus.enumerator == "available").first()
        )
        if not available_status:
            raise HTTPException(status_code=500, detail="Status 'available' not found")

        new_book = Book(
            title=book.title, author=book.author, status_id=available_status.id
        )
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        return new_book

    def get_all(self, db: Session, skip: int = 0, limit: int = 100):
        return db.query(Book).offset(skip).limit(limit).all()

    def get_by_key(self, db: Session, book_key: str):
        try:
            book_key = uuid.UUID(str(book_key))
        except Exception:
            return None

        return db.query(Book).filter(Book.book_key == book_key).first()

    def check_availability(self, db: Session, book_key: str):
        book = self.get_by_key(db, book_key)
        if not book:
            return None

        response = {
            "available": False,
            "status": book.status.enumerator,
            "expected_return_date": None,
        }

        if book.status.enumerator == "available":
            response["available"] = True
            return response

        if book.status.enumerator == "loaned":
            active_loan = (
                db.query(Loan)
                .join(Loan.status)
                .filter(Loan.book_id == book.id, LoanStatus.enumerator == "active")
                .first()
            )

            if active_loan:
                response["expected_return_date"] = active_loan.due_date

        return response
