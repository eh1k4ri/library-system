from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .loan_status import LoanStatusResponse


class LoanEventResponse(BaseModel):
    old_status: Optional[LoanStatusResponse] = None
    new_status: LoanStatusResponse
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
