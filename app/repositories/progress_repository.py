# app/repositories/progress_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from datetime import datetime, timedelta
from app.models.progress import Progress

class ProgressRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> Progress:
        """Create a new progress entry in the database."""
        db_progress = Progress(**kwargs)
        db.add(db_progress)
        db.commit()
        db.refresh(db_progress)
        return db_progress

    @staticmethod
    def get_by_id(db: Session, progress_id: int) -> Optional[Progress]:
        """Get a progress entry by ID."""
        return db.query(Progress).filter(Progress.id == progress_id).first()

    @staticmethod
    def update(db: Session, progress: Progress, **kwargs) -> Progress:
        """Update a progress entry's attributes."""
        for key, value in kwargs.items():
            if hasattr(progress, key) and value is not None:
                setattr(progress, key, value)
        
        db.commit()
        db.refresh(progress)
        return progress

    @staticmethod
    def delete(db: Session, progress_id: int) -> bool:
        """Delete a progress entry by ID."""
        progress = db.query(Progress).filter(Progress.id == progress_id).first()
        if progress:
            db.delete(progress)
            db.commit()
            return True
        return False

    @staticmethod
    def get_by_goal_id(
        db: Session, 
        goal_id: int, 
        skip: int = 0, 
        limit: int = 100,
        sort_by: str = "date",
        sort_desc: bool = True
    ) -> List[Progress]:
        """Get progress entries for a goal with sorting."""
        query = db.query(Progress).filter(Progress.goal_id == goal_id)
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Progress, sort_by)))
        else:
            query = query.order_by(asc(getattr(Progress, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_by_goal_id(db: Session, goal_id: int) -> int:
        """Count progress entries for a goal."""
        return db.query(Progress).filter(Progress.goal_id == goal_id).count()

    @staticmethod
    def get_latest_progress(db: Session, goal_id: int) -> Optional[Progress]:
        """Get the latest progress entry for a goal."""
        return db.query(Progress)\
            .filter(Progress.goal_id == goal_id)\
            .order_by(desc(Progress.date))\
            .first()

    @staticmethod
    def get_progress_trend(db: Session, goal_id: int, days: int = 30) -> List[Progress]:
        """Get progress trend for the last X days."""
        date_threshold = datetime.now() - timedelta(days=days)
        
        return db.query(Progress)\
            .filter(Progress.goal_id == goal_id, Progress.date >= date_threshold)\
            .order_by(asc(Progress.date))\
            .all()