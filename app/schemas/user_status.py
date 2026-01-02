from pydantic import BaseModel


class UserStatusBase(BaseModel):
    enumerator: str
    translation: str


class UserStatusResponse(UserStatusBase):
    class Config:
        from_attributes = True
