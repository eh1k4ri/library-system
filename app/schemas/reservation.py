from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from .reservation_status import ReservationStatusResponse
from .book import BookResponse
from .user import UserResponse


class ReservationCreate(BaseModel):
    user_key: UUID = Field(description="UUID of the user making the reservation")
    book_key: UUID = Field(description="UUID of the book to reserve")


class ReservationResponse(BaseModel):
    reservation_key: UUID = Field(description="Reservation UUID key")
    reserved_at: datetime = Field(description="Reservation creation timestamp")
    expires_at: Optional[datetime] = Field(None, description="Reservation expiry date")
    completed_at: Optional[datetime] = Field(
        None, description="When the reservation was completed"
    )
    user: UserResponse = Field(description="User who made the reservation")
    book: BookResponse = Field(description="Reserved book")
    status: ReservationStatusResponse = Field(description="Reservation status")

    model_config = ConfigDict(from_attributes=True)
