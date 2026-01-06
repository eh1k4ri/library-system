from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.book import BookCreate, BookResponse, BookAvailabilityResponse
from app.services.book_service import BookService
from app.api.deps import PaginationParams
from app.core.errors import BookNotFound

router = APIRouter()
service = BookService()


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return service.create(db=db, book=book)


@router.get("/", response_model=List[BookResponse])
def get_books(pagination: PaginationParams = Depends(), db: Session = Depends(get_db)):
    return service.get_all(db=db, skip=pagination.skip, limit=pagination.per_page)


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
