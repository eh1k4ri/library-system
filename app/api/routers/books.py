from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import PaginationParams
from app.core.errors import BookNotFound, InvalidStatus
from app.db.session import get_session
from app.schemas.book import (
    BookAvailabilityResponse,
    BookCreate,
    BookResponse,
    BookUpdate,
)
from app.services.book_service import BookService

router = APIRouter()
service = BookService()


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, session: Session = Depends(get_session)):
    return service.create(session=session, book=book)


@router.patch("/{book_key}", response_model=BookResponse)
def update_book(
    book_key: str, payload: BookUpdate, session: Session = Depends(get_session)
):
    updated = service.update(session=session, book_key=book_key, data=payload)
    if not updated:
        raise BookNotFound()
    return updated


@router.post("/{book_key}/status", response_model=BookResponse)
def change_book_status(
    book_key: str, status_enum: str, session: Session = Depends(get_session)
):
    updated = service.set_status(
        session=session, book_key=book_key, status_enum=status_enum
    )
    if not updated:
        raise InvalidStatus()
    return updated


@router.get("/", response_model=List[BookResponse])
def get_books(
    pagination: PaginationParams = Depends(),
    genre: str = None,
    session: Session = Depends(get_session),
):
    return service.get_all(
        session=session, skip=pagination.skip, limit=pagination.per_page, genre=genre
    )


@router.get("/genres", response_model=List[str])
def get_genres(session: Session = Depends(get_session)):
    return service.get_genres(session=session)


@router.get("/{book_key}", response_model=BookResponse)
def get_book(book_key: str, session: Session = Depends(get_session)):
    book = service.get_by_key(session=session, book_key=book_key)
    if book is None:
        raise BookNotFound()
    return book


@router.get("/{book_key}/availability", response_model=BookAvailabilityResponse)
def check_book_availability(book_key: str, session: Session = Depends(get_session)):
    result = service.check_availability(session, book_key)
    if result is None:
        raise BookNotFound()
    return result
