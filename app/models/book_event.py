from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class BookEvent(Base):
    __tablename__ = "book_events"

    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    old_status_id = Column(Integer, ForeignKey("book_status.id"), nullable=True)
    new_status_id = Column(Integer, ForeignKey("book_status.id"), nullable=False)
    created_at = Column(DateTime(timezone=True, precision=3), server_default=func.now())

    book = relationship("Book", back_populates="book_events")
    old_status = relationship("BookStatus", foreign_keys=[old_status_id])
    new_status = relationship("BookStatus", foreign_keys=[new_status_id])
