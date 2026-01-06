from sqlalchemy.orm import Session, joinedload
from app.models.book import Book
from app.models.book_status import BookStatus
from app.models.loan import Loan
from app.models.loan_status import LoanStatus
from app.schemas.book import BookCreate
from app.utils.uuid import validate_uuid
from app.utils.cache import get_cache, set_cache


class BookService:
    def create(self, db: Session, book: BookCreate):
        available_status = (
            db.query(BookStatus).filter(BookStatus.enumerator == "available").first()
        )

        new_book = Book(
            title=book.title,
            author=book.author,
            genre=book.genre,
            status_id=available_status.id,
        )
        db.add(new_book)
        db.commit()
        db.refresh(new_book)
        return new_book

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        genre: str | None = None,
    ):
        query = db.query(Book).options(joinedload(Book.status))

        if genre:
            query = query.filter(Book.genre.ilike(genre))

        return query.offset(skip).limit(limit).all()

    def get_genres(self, db: Session):
        genres = (
            db.query(Book.genre)
            .filter(Book.genre.isnot(None))
            .distinct()
            .order_by(Book.genre)
            .all()
        )
        return [g[0] for g in genres]

    def get_by_key(self, db: Session, book_key: str):
        book_key = validate_uuid(book_key)
        if not book_key:
            return None

        cache_key = f"book:{book_key}:details"
        cached_book = get_cache(cache_key)
        if cached_book:
            return cached_book

        book = (
            db.query(Book)
            .options(joinedload(Book.status))
            .filter(Book.book_key == book_key)
            .first()
        )

        if book:
            set_cache(cache_key, book, ttl_seconds=60)

        return book

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
