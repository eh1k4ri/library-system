from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload
from app.models.book import Book
from app.models.book_status import BookStatus
from app.models.loan import Loan
from app.models.loan_status import LoanStatus
from app.schemas.book import BookCreate, BookUpdate
from app.core.constants import CACHE_ENTITY_TTL
from app.utils.uuid import validate_uuid
from app.utils.cache import get_cache, set_cache, clear_cache


class BookService:
    def create(self, session: Session, book: BookCreate):
        available_status = (
            session.query(BookStatus)
            .filter(BookStatus.enumerator == "available")
            .first()
        )

        new_book = Book(
            title=book.title,
            author=book.author,
            genre=book.genre,
            status_id=available_status.id,
        )
        session.add(new_book)
        session.commit()
        session.refresh(new_book)
        
        return new_book

    def get_all(
        self,
        session: Session,
        skip: int = 0,
        limit: int = 100,
        genre: str | None = None,
    ):
        query = session.query(Book).options(joinedload(Book.status))

        if genre:
            query = query.filter(Book.genre.ilike(genre))

        return query.offset(skip).limit(limit).all()

    def get_genres(self, session: Session):
        genre_query = (
            select(Book.genre)
            .where(Book.genre.isnot(None))
            .distinct()
            .order_by(Book.genre)
        )

        return session.execute(genre_query).scalars().all()

    def get_by_key(self, session: Session, book_key: str):
        book_key = validate_uuid(book_key)
        if not book_key:
            return None

        cache_key = f"book:{book_key}:details"

        cached_book = get_cache(cache_key)
        if cached_book:
            return cached_book

        book = (
            session.query(Book)
            .options(joinedload(Book.status))
            .filter(Book.book_key == book_key)
            .first()
        )

        if book:
            set_cache(cache_key, book, ttl_seconds=CACHE_ENTITY_TTL)

        return book

    def _get_for_update(self, session: Session, book_key: str) -> Book | None:
        uuid = validate_uuid(book_key)
        if not uuid:
            return None

        return session.query(Book).filter(Book.book_key == uuid).first()

    def update(self, session: Session, book_key: str, data: BookUpdate):
        book = self._get_for_update(session, book_key)

        if not book:
            return None

        if data.title is not None:
            book.title = data.title
        if data.author is not None:
            book.author = data.author
        if data.genre is not None:
            book.genre = data.genre

        session.commit()
        session.refresh(book)

        set_cache(f"book:{book_key}:details", book, ttl_seconds=CACHE_ENTITY_TTL)

        return book

    def set_status(self, session: Session, book_key: str, status_enum: str):
        book = self._get_for_update(session, book_key)
        if not book:
            return None

        status = (
            session.query(BookStatus)
            .filter(BookStatus.enumerator == status_enum)
            .first()
        )
        if not status:
            return None

        book.status_id = status.id
        session.commit()
        session.refresh(book)

        clear_cache(f"book:{book_key}:details")

        return book

    def check_availability(self, session: Session, book_key: str):
        book = self.get_by_key(session, book_key)

        if not book:
            return None

        status_enum = book.status.enumerator
        book_id = book.id

        response = {
            "available": False,
            "status": status_enum,
            "expected_return_date": None,
        }

        if status_enum == "available":
            response["available"] = True
            return response

        if status_enum == "loaned":
            active_loan = (
                session.query(Loan)
                .join(Loan.status)
                .filter(Loan.book_id == book_id, LoanStatus.enumerator == "active")
                .first()
            )

            if active_loan:
                response["expected_return_date"] = active_loan.due_date

        return response
