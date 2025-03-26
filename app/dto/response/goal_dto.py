# app/dto/response/goal_dto.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.goal import GoalStatus, GoalType

class GoalResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str] = None
    goal_type: GoalType
    target_value: Optional[float] = None
    start_date: datetime
    deadline: Optional[datetime] = None
    status: GoalStatus
    is_public: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    completion_percentage: Optional[float] = None
    
    class Config:
        orm_mode = True

class GoalDetailResponse(GoalResponse):
    progress_history: Optional[List] = []
    latest_progress: Optional[float] = None
    time_remaining: Optional[int] = None  # In days
    is_on_track: Optional[bool] = None

class GoalListResponse(BaseModel):
    items: List[GoalResponse]
    total: int
    page: int
    size: int
    pages: int