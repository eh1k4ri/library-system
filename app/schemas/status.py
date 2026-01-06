from pydantic import BaseModel, ConfigDict


class StatusResponse(BaseModel):
    enumerator: str
    translation: str
    model_config = ConfigDict(from_attributes=True)
