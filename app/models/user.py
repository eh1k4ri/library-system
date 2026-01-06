import uuid
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.types import Uuid as SQLAlchemyUuid
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.session import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_key = Column(
        SQLAlchemyUuid(as_uuid=True),
        default=uuid.uuid4,
        unique=True,
        index=True,
        nullable=False,
    )
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    status_id = Column(Integer, ForeignKey("user_status.id"), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True, precision=3), server_default=func.now()
    )

    loans = relationship("Loan", back_populates="user")
    reservations = relationship("Reservation", back_populates="user")
    status = relationship("UserStatus", back_populates="users")
    user_events = relationship(
        "UserEvent", back_populates="user", cascade="all, delete-orphan"
    )
