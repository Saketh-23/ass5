# File path: app/dto/response/forum_dto.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.dto.response.user_dto import UserResponse

class ForumResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    member_count: Optional[int] = 0
    discussion_count: Optional[int] = 0

    class Config:
        orm_mode = True

class ForumDetailResponse(ForumResponse):
    creator: Optional[UserResponse] = None

class ForumListResponse(BaseModel):
    items: List[ForumResponse]
    total: int
    page: int
    size: int
    pages: int