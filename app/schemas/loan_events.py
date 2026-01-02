from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .loan_status import LoanStatusResponse


class LoanEventResponse(BaseModel):
    old_status: Optional[LoanStatusResponse] = None
    new_status: LoanStatusResponse
    created_at: datetime

    class Config:
        from_attributes = True
