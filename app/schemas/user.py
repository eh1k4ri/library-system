from pydantic import BaseModel, EmailStr
from datetime import datetime
from uuid import UUID
from typing import Optional
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

    class Config:
        from_attributes = True
