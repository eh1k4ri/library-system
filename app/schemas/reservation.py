from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional
from uuid import UUID
from .status import StatusResponse
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
        None, description="When the reservation was completed/picked up"
    )
    user: UserResponse = Field(description="User details")
    book: BookResponse = Field(description="Book details")
    status: StatusResponse = Field(description="Reservation status details")

    model_config = ConfigDict(from_attributes=True)
