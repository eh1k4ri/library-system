from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.book import (
    BookCreate,
    BookResponse,
    BookAvailabilityResponse,
    BookUpdate,
)
from app.services.book_service import BookService
from app.api.deps import PaginationParams
from app.core.errors import BookNotFound

router = APIRouter()
service = BookService()


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return service.create(db=db, book=book)


@router.patch("/{book_key}", response_model=BookResponse)
def update_book(book_key: str, payload: BookUpdate, db: Session = Depends(get_db)):
    updated = service.update(db=db, book_key=book_key, data=payload)
    if not updated:
        raise BookNotFound()
    return updated


@router.post("/{book_key}/status", response_model=BookResponse)
def change_book_status(book_key: str, status_enum: str, db: Session = Depends(get_db)):
    updated = service.set_status(db=db, book_key=book_key, status_enum=status_enum)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status"
        )
    return updated


@router.get("/", response_model=List[BookResponse])
def get_books(
    pagination: PaginationParams = Depends(),
    genre: str | None = None,
    db: Session = Depends(get_db),
):
    return service.get_all(
        db=db, skip=pagination.skip, limit=pagination.per_page, genre=genre
    )


@router.get("/genres", response_model=List[str])
def get_genres(db: Session = Depends(get_db)):
    return service.get_genres(db=db)


@router.get("/{book_key}", response_model=BookResponse)
def get_book(book_key: str, db: Session = Depends(get_db)):
    book = service.get_by_key(db=db, book_key=book_key)
    if book is None:
        raise BookNotFound()
    return book


@router.get("/{book_key}/availability", response_model=BookAvailabilityResponse)
def check_book_availability(book_key: str, db: Session = Depends(get_db)):
    result = service.check_availability(db, book_key)
    if result is None:
        raise BookNotFound()
    return result
