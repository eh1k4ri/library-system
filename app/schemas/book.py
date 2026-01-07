from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, FieldValidationInfo, field_validator

from app.utils.text import clean_optional_str, clean_str

from .status import StatusResponse


class BookBase(BaseModel):
    title: str = Field(min_length=1, max_length=200, description="Book title")
    author: str = Field(min_length=1, max_length=200, description="Author name")
    genre: str = Field(
        default="General", min_length=1, max_length=100, description="Book genre"
    )

    @field_validator("title", "author", "genre")
    @classmethod
    def strip_and_require_content(cls, value: str, info: FieldValidationInfo) -> str:
        return clean_str(value, info.field_name)


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = Field(
        None, min_length=1, max_length=200, description="New title"
    )
    author: Optional[str] = Field(
        None, min_length=1, max_length=200, description="New author"
    )
    genre: Optional[str] = Field(
        None, min_length=1, max_length=100, description="New genre"
    )

    @field_validator("title", "author", "genre")
    @classmethod
    def strip_if_present(
        cls, value: Optional[str], info: FieldValidationInfo
    ) -> Optional[str]:
        return clean_optional_str(value, info.field_name)


class BookAvailabilityResponse(BaseModel):
    available: bool = Field(description="Whether the book is available for loan")
    status: str = Field(description="Current book status enumerator (e.g. 'available')")
    expected_return_date: Optional[datetime] = Field(
        None, description="Expected return date when book is loaned"
    )


class BookResponse(BookBase):
    book_key: UUID = Field(description="Book UUID key")
    created_at: datetime = Field(description="Creation timestamp")
    status: StatusResponse
    model_config = ConfigDict(from_attributes=True)
