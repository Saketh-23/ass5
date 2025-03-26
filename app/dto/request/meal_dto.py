from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.meal_log import MealType

class MealLogCreateRequest(BaseModel):
    meal_type: MealType
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    consumed_at: datetime = Field(default_factory=datetime.now)

class MealLogUpdateRequest(BaseModel):
    meal_type: Optional[MealType] = None
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    consumed_at: Optional[datetime] = None
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None