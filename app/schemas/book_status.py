from pydantic import BaseModel, ConfigDict


class BookStatusBase(BaseModel):
    enumerator: str
    translation: str


class BookStatusResponse(BookStatusBase):
    model_config = ConfigDict(from_attributes=True)
