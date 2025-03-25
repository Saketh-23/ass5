# File path: app/dto/response/comment_dto.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.dto.response.user_dto import UserResponse

class CommentResponse(BaseModel):
    id: int
    discussion_id: int
    user_id: int
    content: str
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    like_count: Optional[int] = 0
    is_liked_by_user: Optional[bool] = False

    class Config:
        orm_mode = True

class CommentDetailResponse(CommentResponse):
    user: Optional[UserResponse] = None
    replies: Optional[List['CommentDetailResponse']] = []

class CommentListResponse(BaseModel):
    items: List[CommentDetailResponse]
    total: int
    page: int
    size: int
    pages: int