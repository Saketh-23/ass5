# File path: app/dto/response/review_dto.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.dto.response.user_dto import UserResponse

class ReviewResponse(BaseModel):
    id: int
    user_id: int
    program_id: int
    rating: float
    comment: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ReviewDetailResponse(ReviewResponse):
    user: Optional[UserResponse] = None

class ReviewListResponse(BaseModel):
    items: List[ReviewResponse]
    total: int
    page: int
    size: int
    pages: int

class ProgramRatingResponse(BaseModel):
    program_id: int
    average_rating: float
    total_reviews: int

class TrainerRatingResponse(BaseModel):
    trainer_id: int
    average_rating: float
    total_reviews: int
    total_programs: int