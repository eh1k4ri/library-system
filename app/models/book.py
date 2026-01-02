import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    book_key = Column(
        UUID(as_uuid=True), default=uuid.uuid4, unique=True, index=True, nullable=False
    )
    title = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False)
    status_id = Column(Integer, ForeignKey("book_status.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    loans = relationship("Loan", back_populates="book")
    status_rel = relationship("BookStatus", back_populates="books")
    book_events = relationship(
        "BookEvent", back_populates="book", cascade="all, delete-orphan"
    )
