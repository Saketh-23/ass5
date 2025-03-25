# File path: app/dto/request/comment_dto.py
from pydantic import BaseModel, Field
from typing import Optional

class CommentCreateRequest(BaseModel):
    discussion_id: int
    content: str = Field(..., min_length=1)
    parent_id: Optional[int] = None

class CommentUpdateRequest(BaseModel):
    content: str = Field(..., min_length=1)