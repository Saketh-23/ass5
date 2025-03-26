# app/dto/response/assessment_dto.py

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class ProgressAssessmentResponse(BaseModel):
    goal_id: int
    completion_percentage: float
    current_value: Optional[float] = None
    target_value: Optional[float] = None
    time_elapsed_percentage: float
    is_on_track: bool
    status_message: str
    feedback: str
    alerts: List[str] = []
    
    class Config:
        orm_mode = True

class ProgressPredictionResponse(BaseModel):
    goal_id: int
    predicted_completion_date: Optional[datetime] = None
    predicted_final_value: Optional[float] = None
    will_meet_deadline: Optional[bool] = None
    days_ahead_behind: Optional[int] = None
    trend: str
    
    class Config:
        orm_mode = True