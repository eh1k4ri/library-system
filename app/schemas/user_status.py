from pydantic import BaseModel, ConfigDict


class UserStatusBase(BaseModel):
    enumerator: str
    translation: str


class UserStatusResponse(UserStatusBase):
    model_config = ConfigDict(from_attributes=True)
