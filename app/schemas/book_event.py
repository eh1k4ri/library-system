from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .book_status import BookStatusResponse


class BookEventResponse(BaseModel):
    old_status: Optional[BookStatusResponse] = None
    new_status: BookStatusResponse
    created_at: datetime

    class Config:
        from_attributes = True
