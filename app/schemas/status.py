from pydantic import BaseModel, ConfigDict, Field


class StatusResponse(BaseModel):
    enumerator: str = Field(min_length=1, max_length=50)
    translation: str = Field(min_length=1, max_length=100)
    model_config = ConfigDict(from_attributes=True)
