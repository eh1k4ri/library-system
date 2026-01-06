from pydantic import BaseModel, ConfigDict, Field, field_validator, FieldValidationInfo
from app.utils.text import clean_str


class StatusBase(BaseModel):
    enumerator: str = Field(min_length=1, max_length=50)
    translation: str = Field(min_length=1, max_length=100)

    @field_validator("enumerator", "translation")
    @classmethod
    def strip_and_require_content(cls, value: str, info: FieldValidationInfo) -> str:
        return clean_str(value, info.field_name)


class StatusResponse(StatusBase):
    model_config = ConfigDict(from_attributes=True)
