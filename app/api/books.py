from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.db.session import get_db
from app.schemas.book import BookCreate, BookResponse
from app.services.book_service import BookService

router = APIRouter()
service = BookService()


@router.post("/", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    return service.create(db=db, book=book)


@router.get("/", response_model=List[BookResponse])
def read_books(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return service.get_all(db=db, skip=skip, limit=limit)
