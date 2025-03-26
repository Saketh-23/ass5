# app/dto/response/achievement_dto.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class AchievementResponse(BaseModel):
    id: int
    user_id: int
    goal_id: Optional[int] = None
    title: str
    description: Optional[str] = None
    badge_url: Optional[str] = None
    is_system: bool
    achieved_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class AchievementDetailResponse(AchievementResponse):
    goal_title: Optional[str] = None

class AchievementListResponse(BaseModel):
    items: List[AchievementResponse]
    total: int
    page: int
    size: int
    pages: int