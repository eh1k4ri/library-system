from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class UserEvent(Base):
    __tablename__ = "user_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    old_status_id = Column(Integer, ForeignKey("user_status.id"), nullable=True)
    new_status_id = Column(Integer, ForeignKey("user_status.id"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True, precision=3), server_default=func.now()
    )

    user = relationship("User", back_populates="user_events")
    old_status = relationship("UserStatus", foreign_keys=[old_status_id])
    new_status = relationship("UserStatus", foreign_keys=[new_status_id])
