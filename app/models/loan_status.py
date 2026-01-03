from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class LoanStatus(Base):
    __tablename__ = "loan_status"

    id = Column(Integer, primary_key=True, index=True)
    enumerator = Column(String, unique=True, index=True, nullable=False)
    translation = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    loans = relationship("Loan", back_populates="status")
