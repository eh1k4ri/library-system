from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.book import Book
from app.models.book_status import BookStatus
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
