from pydantic import (
    BaseModel,
    EmailStr,
    ConfigDict,
    Field,
    field_validator,
    FieldValidationInfo,
)
from datetime import datetime
from uuid import UUID
from typing import Optional
from .status import StatusResponse
from app.utils.text import clean_str, normalize_email


class UserBase(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Full name of the user")
    email: EmailStr = Field(description="User email address")

    @field_validator("name")
    @classmethod
    def strip_and_require_content(cls, value: str, info: FieldValidationInfo) -> str:
        return clean_str(value, info.field_name)

    @field_validator("email")
    @classmethod
    def normalize_email_field(cls, value: EmailStr, info: FieldValidationInfo) -> str:
        return normalize_email(str(value), info.field_name)


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = Field(None)

    @field_validator("name")
    @classmethod
    def strip_name(
        cls, value: Optional[str], info: FieldValidationInfo
    ) -> Optional[str]:
        if value is None:
            return value
        return clean_str(value, info.field_name)

    @field_validator("email")
    @classmethod
    def normalize_email_field_optional(
        cls, value: Optional[EmailStr], info: FieldValidationInfo
    ) -> Optional[str]:
        if value is None:
            return value
        return normalize_email(str(value), info.field_name)


class UserResponse(UserBase):
    user_key: UUID = Field(description="User UUID key")
    created_at: datetime = Field(description="Creation timestamp")
    status: StatusResponse
    model_config = ConfigDict(from_attributes=True)
