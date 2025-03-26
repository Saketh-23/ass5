# app/dto/response/progress_dto.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProgressResponse(BaseModel):
    id: int
    goal_id: int
    date: datetime
    value: float
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class ProgressDetailResponse(ProgressResponse):
    goal_title: Optional[str] = None
    target_value: Optional[float] = None
    percentage: Optional[float] = None


class ProgressListResponse(BaseModel):
    items: List[ProgressResponse]
    total: int
    page: int
    size: int
    pages: int