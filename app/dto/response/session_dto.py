# File path: app/dto/response/session_dto.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.dto.response.user_dto import UserResponse

class SessionResponse(BaseModel):
    id: int
    program_id: int
    trainer_id: int
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    total_slots: int
    available_slots: int
    price: float
    location: Optional[str] = None
    is_virtual: bool
    meeting_link: Optional[str] = None
    is_cancelled: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class SessionDetailResponse(SessionResponse):
    trainer: Optional[UserResponse] = None

class SessionListResponse(BaseModel):
    items: List[SessionResponse]
    total: int
    page: int
    size: int
    pages: int