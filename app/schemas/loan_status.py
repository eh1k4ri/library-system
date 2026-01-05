from pydantic import BaseModel, ConfigDict


class LoanStatusBase(BaseModel):
    enumerator: str
    translation: str


class LoanStatusCreate(LoanStatusBase):
    pass


class LoanStatusResponse(LoanStatusBase):
    model_config = ConfigDict(from_attributes=True)
