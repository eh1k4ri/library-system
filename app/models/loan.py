from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base

class Loan(Base):
    __tablename__ = "loans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("loan_status.id"), nullable=False)
    
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    due_date = Column(DateTime(timezone=True), nullable=False)
    return_date = Column(DateTime(timezone=True), nullable=True)
    fine_amount = Column(Float, default=0.0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="loans")
    book = relationship("Book", back_populates="loans")
    status_rel = relationship("LoanStatus", back_populates="loans")
    
    events = relationship("LoanEvent", back_populates="loan", cascade="all, delete-orphan")
    history = relationship("LoanHistory", back_populates="loan", cascade="all, delete-orphan")