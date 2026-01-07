from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class UserStatus(Base):
    __tablename__ = "user_status"

    id = Column(Integer, primary_key=True, index=True)
    enumerator = Column(String, unique=True, index=True, nullable=False)
    translation = Column(String, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True, precision=3), server_default=func.now()
    )

    users = relationship("User", back_populates="status")
