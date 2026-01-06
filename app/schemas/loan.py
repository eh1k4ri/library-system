from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from .status import StatusResponse
from .loan_event import LoanEventResponse
from .book import BookResponse
from .user import UserResponse


class LoanCreate(BaseModel):
    user_key: UUID = Field(description="UUID of the user taking the loan")
    book_key: UUID = Field(description="UUID of the book to loan")


class LoanResponse(BaseModel):
    loan_key: UUID = Field(description="Loan UUID key")
    start_date: datetime = Field(description="Loan start date")
    due_date: datetime = Field(description="Calculated due date")

    return_date: Optional[datetime] = Field(
        None, description="Return timestamp, if returned"
    )
    fine_amount: float = Field(
        default=0.0, description="Fine amount calculated on return"
    )
    user: UserResponse
    book: BookResponse
    status: StatusResponse
    events: List[LoanEventResponse] = Field(default_factory=list)
    model_config = ConfigDict(from_attributes=True)


class LoanReturnRequest(BaseModel):
    book_key: UUID = Field(description="UUID of the book being returned")
