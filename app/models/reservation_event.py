from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class ReservationEvent(Base):
    __tablename__ = "reservation_events"

    id = Column(Integer, primary_key=True, index=True)
    reservation_id = Column(Integer, ForeignKey("reservations.id"), nullable=False)
    old_status_id = Column(Integer, ForeignKey("reservation_status.id"), nullable=True)
    new_status_id = Column(Integer, ForeignKey("reservation_status.id"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True, precision=3), server_default=func.now()
    )

    reservation = relationship("Reservation", back_populates="events")
    old_status = relationship("ReservationStatus", foreign_keys=[old_status_id])
    new_status = relationship("ReservationStatus", foreign_keys=[new_status_id])
