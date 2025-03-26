from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.meal_log import MealType

class MealLogResponse(BaseModel):
    id: int
    user_id: int
    meal_type: MealType
    name: str
    description: Optional[str] = None
    consumed_at: datetime
    calories: Optional[int] = None
    protein: Optional[float] = None
    carbs: Optional[float] = None
    fat: Optional[float] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class MealLogListResponse(BaseModel):
    items: List[MealLogResponse]
    total: int
    page: int
    size: int
    pages: int

class NutritionAnalysisResponse(BaseModel):
    meal_name: str
    calories: int
    protein: float
    carbs: float
    fat: float
    analysis_details: Optional[Dict[str, Any]] = None