# File path: app/dto/response/membership_dto.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.forum_membership import MembershipStatus, MembershipRole
from app.dto.response.user_dto import UserResponse

class MembershipResponse(BaseModel):
    id: int
    forum_id: int
    user_id: int
    join_date: datetime
    status: MembershipStatus
    role: MembershipRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class MembershipDetailResponse(MembershipResponse):
    user: Optional[UserResponse] = None

class MembershipListResponse(BaseModel):
    items: List[MembershipDetailResponse]
    total: int
    page: int
    size: int
    pages: int