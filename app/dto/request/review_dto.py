# File path: app/dto/request/review_dto.py
from pydantic import BaseModel, Field, validator
from typing import Optional

class ReviewCreateRequest(BaseModel):
    program_id: int
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating from 1.0 to 5.0")
    comment: Optional[str] = None

class ReviewUpdateRequest(BaseModel):
    rating: Optional[float] = Field(None, ge=1.0, le=5.0, description="Rating from 1.0 to 5.0")
    comment: Optional[str] = None