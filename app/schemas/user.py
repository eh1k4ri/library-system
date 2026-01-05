from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from uuid import UUID
from .user_status import UserStatusResponse


class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    user_key: UUID
    created_at: datetime
    status: UserStatusResponse

    model_config = ConfigDict(from_attributes=True)
