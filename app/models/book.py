from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func, expression # Importar expression
from app.db.session import Base

class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False)
    is_available = Column(Boolean, default=True)
    is_active = Column(Boolean, default=True, server_default=expression.true(), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    loans = relationship("Loan", back_populates="book")