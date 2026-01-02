from pydantic import BaseModel


class LoanStatusBase(BaseModel):
    enumerator: str
    translation: str


class LoanStatusCreate(LoanStatusBase):
    pass


class LoanStatusResponse(LoanStatusBase):
    class Config:
        from_attributes = True
