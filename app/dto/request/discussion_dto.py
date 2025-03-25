# File path: app/dto/request/discussion_dto.py
from pydantic import BaseModel, Field
from typing import Optional

class DiscussionCreateRequest(BaseModel):
    forum_id: int
    title: str = Field(..., min_length=5, max_length=200)
    content: str = Field(..., min_length=10)

class DiscussionUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=5, max_length=200)
    content: Optional[str] = Field(None, min_length=10)