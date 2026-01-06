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
from .user_status import UserStatusResponse
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
    def normalize_email_field(
        cls, value: EmailStr, info: FieldValidationInfo
    ) -> EmailStr:
        normalized = normalize_email(str(value), info.field_name)
        return normalized


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int = Field(description="Internal user identifier")
    user_key: UUID = Field(description="User UUID key")
    created_at: datetime = Field(description="Creation timestamp")
    status: UserStatusResponse

    model_config = ConfigDict(from_attributes=True)
