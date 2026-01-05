from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from .book import BookResponse
from .user import UserResponse
from .loan_status import LoanStatusResponse
from .loan_event import LoanEventResponse


class LoanCreate(BaseModel):
    user_key: UUID
    book_key: UUID
    days: int = 7


class LoanResponse(BaseModel):
    loan_key: UUID
    start_date: datetime
    due_date: datetime
    return_date: Optional[datetime] = None
    fine_amount: float

    user: UserResponse
    book: BookResponse
    status: LoanStatusResponse
    loan_events: List[LoanEventResponse] = []

    class Config:
        from_attributes = True
