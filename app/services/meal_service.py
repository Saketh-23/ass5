from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, date

from app.models.user import User
from app.models.meal_log import MealLog, MealType
from app.dto.request.meal_dto import MealLogCreateRequest, MealLogUpdateRequest
from app.repositories.meal_repository import MealRepository
from app.services.ai_service import AIService

class MealService:
    @staticmethod
    def create_meal_log(db: Session, meal_data: MealLogCreateRequest, user: User) -> MealLog:
        """Create a new meal log with AI-calculated nutrition data."""
        # Use AI to analyze nutrition content
        nutrition_analysis = AIService.analyze_meal_nutrition(
            meal_name=meal_data.name,
            meal_description=meal_data.description
        )
        
        # Create the meal log with the analyzed data
        meal = MealRepository.create(
            db=db,
            user_id=user.id,
            meal_type=meal_data.meal_type,
            name=meal_data.name,
            description=meal_data.description,
            consumed_at=meal_data.consumed_at,
            calories=nutrition_analysis.get("calories"),
            protein=nutrition_analysis.get("protein"),
            carbs=nutrition_analysis.get("carbs"),
            fat=nutrition_analysis.get("fat")
        )
        
        return meal

    @staticmethod
    def get_meal_log(db: Session, meal_id: int, user_id: int) -> MealLog:
        """Get a meal log by ID, ensuring it belongs to the user."""
        meal = MealRepository.get_by_id(db, meal_id)
        if not meal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Meal log not found",
            )
        
        if meal.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this meal log",
            )
        
        return meal

    @staticmethod
    def update_meal_log(db: Session, meal_id: int, meal_data: MealLogUpdateRequest, user: User) -> MealLog:
        """Update a meal log."""
        meal = MealService.get_meal_log(db, meal_id, user.id)
        
        # Update meal log
        updated_meal = MealRepository.update(
            db=db,
            meal=meal,
            meal_type=meal_data.meal_type,
            name=meal_data.name,
            description=meal_data.description,
            consumed_at=meal_data.consumed_at,
            calories=meal_data.calories,
            protein=meal_data.protein,
            carbs=meal_data.carbs,
            fat=meal_data.fat
        )
        
        return updated_meal

    @staticmethod
    def delete_meal_log(db: Session, meal_id: int, user: User) -> bool:
        """Delete a meal log."""
        meal = MealService.get_meal_log(db, meal_id, user.id)
        return MealRepository.delete(db, meal_id)

    @staticmethod
    def get_user_meal_logs(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        meal_type: Optional[MealType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: str = "consumed_at",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Get all meal logs for a user with pagination, filtering, and sorting."""
        meals = MealRepository.get_by_user_id(
            db, user_id, skip=skip, limit=limit, 
            meal_type=meal_type, start_date=start_date, end_date=end_date,
            sort_by=sort_by, sort_desc=sort_desc
        )
        
        total = MealRepository.count_by_user_id(
            db, user_id, meal_type=meal_type, start_date=start_date, end_date=end_date
        )
        
        return {
            "items": meals,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def get_daily_nutrition(db: Session, user_id: int, query_date: date) -> Dict[str, Any]:
        """Get nutrition summary for a specific day."""
        # Convert date to datetime for query
        datetime_date = datetime.combine(query_date, datetime.min.time())
        
        return MealRepository.get_daily_nutrition(db, user_id, datetime_date)