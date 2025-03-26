from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatMessageResponse(BaseModel):
    id: int
    is_user_message: bool
    content: str
    created_at: datetime

    class Config:
        orm_mode = True

class ChatHistoryResponse(BaseModel):
    messages: List[ChatMessageResponse]
    total: int

class DietPlanResponse(BaseModel):
    diet_plan: str
    request: str

class WorkoutPlanResponse(BaseModel):
    workout_plan: str
    request: str