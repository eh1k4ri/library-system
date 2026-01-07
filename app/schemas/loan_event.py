from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .status import StatusResponse


class LoanEventResponse(BaseModel):
    old_status: Optional[StatusResponse] = Field(
        default=None, description="Previous loan status, if any"
    )
    new_status: StatusResponse = Field(description="Current loan status")
    created_at: datetime = Field(description="When the status change was recorded")
    model_config = ConfigDict(from_attributes=True)
