from pydantic import BaseModel
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from .book_status import BookStatusResponse


class BookBase(BaseModel):
    title: str
    author: str


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None


class BookResponse(BookBase):
    book_key: UUID
    created_at: datetime
    status_rel: BookStatusResponse

    class Config:
        from_attributes = True
