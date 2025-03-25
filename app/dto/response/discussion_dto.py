# File path: app/dto/response/discussion_dto.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.dto.response.user_dto import UserResponse
from app.dto.response.forum_dto import ForumResponse

class DiscussionResponse(BaseModel):
    id: int
    forum_id: int
    user_id: int
    title: str
    content: str
    is_pinned: bool
    is_locked: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    comment_count: Optional[int] = 0

    class Config:
        orm_mode = True

class DiscussionDetailResponse(DiscussionResponse):
    user: Optional[UserResponse] = None
    forum: Optional[ForumResponse] = None

class DiscussionListResponse(BaseModel):
    items: List[DiscussionResponse]
    total: int
    page: int
    size: int
    pages: int