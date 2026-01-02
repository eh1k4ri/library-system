from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from .user_status import UserStatusResponse


class UserEventResponse(BaseModel):
    old_status: Optional[UserStatusResponse] = None
    new_status: UserStatusResponse
    created_at: datetime

    class Config:
        from_attributes = True
