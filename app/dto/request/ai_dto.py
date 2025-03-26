from pydantic import BaseModel, Field
from typing import Optional, List

class ChatMessageRequest(BaseModel):
    message: str = Field(..., min_length=1)

class DietPlanRequest(BaseModel):
    user_input: str = Field(..., min_length=1)
    
class WorkoutPlanRequest(BaseModel):
    user_input: str = Field(..., min_length=1)