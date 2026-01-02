from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class BookBase(BaseModel):
    title: str
    author: str


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    is_available: Optional[bool] = None


class BookResponse(BookBase):
    id: int
    is_available: bool
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True
