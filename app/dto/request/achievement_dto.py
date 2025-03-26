# File path: app/dto/request/achievement_dto.py
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# This would typically only be used by admins to create system achievements
class AchievementCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    badge_url: Optional[str] = None
    is_system: bool = True