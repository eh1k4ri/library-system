from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.types import Uuid as SQLAlchemyUuid
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base
import uuid


class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)

    reservation_key = Column(
        SQLAlchemyUuid(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        index=True,
        nullable=False,
    )
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    status_id = Column(Integer, ForeignKey("reservation_status.id"), nullable=False)
    reserved_at = Column(
        TIMESTAMP(timezone=True, precision=3), server_default=func.now(), nullable=False
    )
    expires_at = Column(TIMESTAMP(timezone=True, precision=3), nullable=True)
    completed_at = Column(TIMESTAMP(timezone=True, precision=3), nullable=True)

    user = relationship("User", back_populates="reservations")
    book = relationship("Book", back_populates="reservations")
    status = relationship("ReservationStatus")
