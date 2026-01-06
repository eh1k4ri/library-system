from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.sql import func
from app.db.session import Base


class ReservationStatus(Base):
    __tablename__ = "reservation_status"

    id = Column(Integer, primary_key=True, index=True)
    enumerator = Column(String, unique=True, nullable=False)
    translation = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True, precision=3), server_default=func.now()
    )
