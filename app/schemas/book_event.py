from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .book_status import BookStatusResponse


class BookEventResponse(BaseModel):
    old_status: Optional[BookStatusResponse] = None
    new_status: BookStatusResponse
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
