# File path: app/dto/request/booking_dto.py
from pydantic import BaseModel, Field
from typing import Optional
from app.models.booking import BookingStatus

class BookingCreateRequest(BaseModel):
    session_id: int

class BookingUpdateRequest(BaseModel):
    status: Optional[BookingStatus] = None
    attended: Optional[bool] = None