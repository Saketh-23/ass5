from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from datetime import datetime, timedelta
from app.models.meal_log import MealLog, MealType

class MealRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> MealLog:
        """Create a new meal log in the database."""
        db_meal = MealLog(**kwargs)
        db.add(db_meal)
        db.commit()
        db.refresh(db_meal)
        return db_meal

    @staticmethod
    def get_by_id(db: Session, meal_id: int) -> Optional[MealLog]:
        """Get a meal log by ID."""
        return db.query(MealLog).filter(MealLog.id == meal_id).first()

    @staticmethod
    def update(db: Session, meal: MealLog, **kwargs) -> MealLog:
        """Update a meal log's attributes."""
        for key, value in kwargs.items():
            if hasattr(meal, key) and value is not None:
                setattr(meal, key, value)
        
        db.commit()
        db.refresh(meal)
        return meal

    @staticmethod
    def delete(db: Session, meal_id: int) -> bool:
        """Delete a meal log by ID."""
        meal = db.query(MealLog).filter(MealLog.id == meal_id).first()
        if meal:
            db.delete(meal)
            db.commit()
            return True
        return False

    @staticmethod
    def get_by_user_id(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        meal_type: Optional[MealType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        sort_by: str = "consumed_at",
        sort_desc: bool = True
    ) -> List[MealLog]:
        """Get meal logs by user ID with filtering and sorting."""
        query = db.query(MealLog).filter(MealLog.user_id == user_id)
        
        # Apply filters
        if meal_type:
            query = query.filter(MealLog.meal_type == meal_type)
            
        if start_date:
            query = query.filter(MealLog.consumed_at >= start_date)
            
        if end_date:
            query = query.filter(MealLog.consumed_at <= end_date)
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(MealLog, sort_by)))
        else:
            query = query.order_by(asc(getattr(MealLog, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_by_user_id(
        db: Session, 
        user_id: int,
        meal_type: Optional[MealType] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """Count meal logs by user ID with filtering."""
        query = db.query(MealLog).filter(MealLog.user_id == user_id)
        
        # Apply filters
        if meal_type:
            query = query.filter(MealLog.meal_type == meal_type)
            
        if start_date:
            query = query.filter(MealLog.consumed_at >= start_date)
            
        if end_date:
            query = query.filter(MealLog.consumed_at <= end_date)
            
        return query.count()

    @staticmethod
    def get_recent_meals(db: Session, user_id: int, days: int = 7) -> List[MealLog]:
        """Get meals from the last X days for a specific user."""
        start_date = datetime.now() - timedelta(days=days)
        return MealRepository.get_by_user_id(
            db, 
            user_id, 
            start_date=start_date,
            limit=100,  # Get more data for analysis
            sort_desc=False  # Chronological order
        )

    @staticmethod
    def get_daily_nutrition(db: Session, user_id: int, date: datetime) -> Dict[str, Any]:
        """Get total nutrition for a specific day."""
        start_of_day = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_of_day = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        meals = MealRepository.get_by_user_id(
            db, 
            user_id, 
            start_date=start_of_day,
            end_date=end_of_day,
            limit=50  # Reasonable max for one day
        )
        
        # Calculate totals
        total_calories = sum(meal.calories or 0 for meal in meals)
        total_protein = sum(meal.protein or 0 for meal in meals)
        total_carbs = sum(meal.carbs or 0 for meal in meals)
        total_fat = sum(meal.fat or 0 for meal in meals)
        
        return {
            "date": date.date(),
            "total_calories": total_calories,
            "total_protein": total_protein,
            "total_carbs": total_carbs,
            "total_fat": total_fat,
            "meal_count": len(meals),
            "meals": [{"id": meal.id, "name": meal.name, "meal_type": meal.meal_type.value} for meal in meals]
        }