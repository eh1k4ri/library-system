from pydantic import BaseModel


class BookStatusBase(BaseModel):
    enumerator: str
    translation: str


class BookStatusResponse(BookStatusBase):
    class Config:
        from_attributes = True
