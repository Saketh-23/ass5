# app/repositories/achievement_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from datetime import datetime
from app.models.achievement import Achievement

class AchievementRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> Achievement:
        """Create a new achievement in the database."""
        db_achievement = Achievement(**kwargs)
        db.add(db_achievement)
        db.commit()
        db.refresh(db_achievement)
        return db_achievement

    @staticmethod
    def get_by_id(db: Session, achievement_id: int) -> Optional[Achievement]:
        """Get an achievement by ID."""
        return db.query(Achievement).filter(Achievement.id == achievement_id).first()

    @staticmethod
    def update(db: Session, achievement: Achievement, **kwargs) -> Achievement:
        """Update an achievement's attributes."""
        for key, value in kwargs.items():
            if hasattr(achievement, key) and value is not None:
                setattr(achievement, key, value)
        
        db.commit()
        db.refresh(achievement)
        return achievement

    @staticmethod
    def delete(db: Session, achievement_id: int) -> bool:
        """Delete an achievement by ID."""
        achievement = db.query(Achievement).filter(Achievement.id == achievement_id).first()
        if achievement:
            db.delete(achievement)
            db.commit()
            return True
        return False

    @staticmethod
    def get_by_user_id(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        sort_by: str = "achieved_date",
        sort_desc: bool = True
    ) -> List[Achievement]:
        """Get achievements by user ID with sorting."""
        query = db.query(Achievement).filter(Achievement.user_id == user_id)
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Achievement, sort_by)))
        else:
            query = query.order_by(asc(getattr(Achievement, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_by_user_id(db: Session, user_id: int) -> int:
        """Count achievements by user ID."""
        return db.query(Achievement).filter(Achievement.user_id == user_id).count()

    @staticmethod
    def get_by_goal_id(db: Session, goal_id: int) -> List[Achievement]:
        """Get achievements related to a specific goal."""
        return db.query(Achievement).filter(Achievement.goal_id == goal_id).all()

    @staticmethod
    def check_achievement_exists(
        db: Session, 
        user_id: int, 
        title: str
    ) -> bool:
        """Check if a user already has an achievement with the given title."""
        achievement = db.query(Achievement)\
            .filter(Achievement.user_id == user_id, Achievement.title == title)\
            .first()
            
        return achievement is not None