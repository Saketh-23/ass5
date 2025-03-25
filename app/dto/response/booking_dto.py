# File path: app/dto/response/booking_dto.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.booking import BookingStatus
from app.dto.response.session_dto import SessionResponse
from app.dto.response.user_dto import UserResponse

class BookingResponse(BaseModel):
    id: int
    user_id: int
    session_id: int
    booking_date: datetime
    status: BookingStatus
    attended: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class BookingDetailResponse(BookingResponse):
    session: Optional[SessionResponse] = None
    user: Optional[UserResponse] = None

class BookingListResponse(BaseModel):
    items: List[BookingResponse]
    total: int
    page: int
    size: int
    pages: int