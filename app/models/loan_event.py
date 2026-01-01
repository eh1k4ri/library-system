from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class LoanEvent(Base):
    __tablename__ = "loan_events"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id"), nullable=False)

    old_status_id = Column(Integer, ForeignKey("loan_status.id"), nullable=True)
    new_status_id = Column(Integer, ForeignKey("loan_status.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    loan = relationship("Loan", back_populates="events")
    old_status = relationship("LoanStatus", foreign_keys=[old_status_id])
    new_status = relationship("LoanStatus", foreign_keys=[new_status_id])
