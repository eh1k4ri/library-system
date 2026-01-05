from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
from .user_status import UserStatusResponse


class UserEventResponse(BaseModel):
    old_status: Optional[UserStatusResponse] = None
    new_status: UserStatusResponse
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
