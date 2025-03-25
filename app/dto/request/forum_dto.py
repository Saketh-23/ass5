# File path: app/dto/request/forum_dto.py
from pydantic import BaseModel, Field
from typing import Optional

class ForumCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None

class ForumUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    is_active: Optional[bool] = None