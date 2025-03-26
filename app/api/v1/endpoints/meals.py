from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.meal_log import MealType
from app.dto.request.meal_dto import MealLogCreateRequest, MealLogUpdateRequest
from app.dto.response.meal_dto import MealLogResponse, MealLogListResponse, NutritionAnalysisResponse
from app.services.meal_service import MealService
from app.services.ai_service import AIService

router = APIRouter(prefix="/meals", tags=["Meal Tracking"])

@router.post("", response_model=MealLogResponse, status_code=status.HTTP_201_CREATED)
def create_meal_log(
    meal_data: MealLogCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Log a new meal with automatic nutrition calculation."""
    meal = MealService.create_meal_log(db, meal_data, current_user)
    return meal

@router.get("", response_model=MealLogListResponse)
def get_my_meals(
    meal_type: Optional[MealType] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("consumed_at", regex="^(consumed_at|meal_type|calories)$"),
    sort_desc: bool = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user's meal logs with filtering and sorting."""
    # Convert dates to datetime objects
    start_datetime = datetime.combine(start_date, datetime.min.time()) if start_date else None
    end_datetime = datetime.combine(end_date, datetime.max.time()) if end_date else None
    
    result = MealService.get_user_meal_logs(
        db, current_user.id, skip=skip, limit=limit, 
        meal_type=meal_type, start_date=start_datetime, end_date=end_datetime,
        sort_by=sort_by, sort_desc=sort_desc
    )
    
    return result

@router.get("/{meal_id}", response_model=MealLogResponse)
def get_meal(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific meal log."""
    meal = MealService.get_meal_log(db, meal_id, current_user.id)
    return meal

@router.put("/{meal_id}", response_model=MealLogResponse)
def update_meal(
    meal_id: int,
    meal_data: MealLogUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a meal log."""
    meal = MealService.update_meal_log(db, meal_id, meal_data, current_user)
    return meal

@router.delete("/{meal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_meal(
    meal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a meal log."""
    MealService.delete_meal_log(db, meal_id, current_user)
    return None

@router.post("/analyze", response_model=NutritionAnalysisResponse)
def analyze_meal(
    meal_data: Dict[str, str],
    current_user: User = Depends(get_current_user),
):
    """Analyze a meal without saving it."""
    nutrition = AIService.analyze_meal_nutrition(
        meal_name=meal_data.get("name", ""),
        meal_description=meal_data.get("description", "")
    )
    
    # Ensure analysis_details is a dictionary
    analysis_details = nutrition.get("analysis_details", {})
    if not isinstance(analysis_details, dict):
        analysis_details = {"summary": str(analysis_details)}
    
    # Format the response
    return {
        "meal_name": meal_data.get("name", ""),
        "calories": nutrition.get("calories", 0),
        "protein": nutrition.get("protein", 0.0),
        "carbs": nutrition.get("carbs", 0.0),
        "fat": nutrition.get("fat", 0.0),
        "analysis_details": analysis_details
    }

@router.get("/daily/{date}", response_model=Dict[str, Any])
def get_daily_nutrition(
    date: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get nutrition summary for a specific day."""
    daily_data = MealService.get_daily_nutrition(db, current_user.id, date)
    return daily_data