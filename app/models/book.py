import uuid
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.types import Uuid as SQLAlchemyUuid

from app.db.session import Base


class Book(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)

    book_key = Column(
        SQLAlchemyUuid(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        index=True,
        nullable=False,
    )

    title = Column(String, index=True, nullable=False)
    author = Column(String, nullable=False)
    status_id = Column(Integer, ForeignKey("book_status.id"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True, precision=3), server_default=func.now()
    )

    status = relationship("BookStatus", back_populates="books")
    loans = relationship("Loan", back_populates="book")
    book_events = relationship(
        "BookEvent", back_populates="book", cascade="all, delete-orphan"
    )
