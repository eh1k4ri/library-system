from pydantic import BaseModel, ConfigDict
from datetime import datetime
from uuid import UUID
from typing import Optional
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
    status: BookStatusResponse

    model_config = ConfigDict(from_attributes=True)
