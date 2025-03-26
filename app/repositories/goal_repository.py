# app/repositories/goal_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from datetime import datetime, timedelta
from app.models.goal import Goal, GoalStatus
from app.models.progress import Progress

class GoalRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> Goal:
        """Create a new goal in the database."""
        db_goal = Goal(**kwargs)
        db.add(db_goal)
        db.commit()
        db.refresh(db_goal)
        return db_goal

    @staticmethod
    def get_by_id(db: Session, goal_id: int) -> Optional[Goal]:
        """Get a goal by ID."""
        return db.query(Goal).filter(Goal.id == goal_id).first()

    @staticmethod
    def update(db: Session, goal: Goal, **kwargs) -> Goal:
        """Update a goal's attributes."""
        for key, value in kwargs.items():
            if hasattr(goal, key) and value is not None:
                setattr(goal, key, value)
        
        db.commit()
        db.refresh(goal)
        return goal

    @staticmethod
    def delete(db: Session, goal_id: int) -> bool:
        """Delete a goal by ID."""
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if goal:
            db.delete(goal)
            db.commit()
            return True
        return False

    @staticmethod
    def get_by_user_id(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> List[Goal]:
        """Get goals by user ID with filtering and sorting."""
        query = db.query(Goal).filter(Goal.user_id == user_id)
        
        # Apply filters
        if filters:
            if "status" in filters and filters["status"]:
                query = query.filter(Goal.status == filters["status"])
                
            if "goal_type" in filters and filters["goal_type"]:
                query = query.filter(Goal.goal_type == filters["goal_type"])
                
            if "is_public" in filters:
                query = query.filter(Goal.is_public == filters["is_public"])
                
            if "start_date_after" in filters and filters["start_date_after"]:
                query = query.filter(Goal.start_date >= filters["start_date_after"])
                
            if "deadline_before" in filters and filters["deadline_before"]:
                query = query.filter(Goal.deadline <= filters["deadline_before"])
                
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                query = query.filter(Goal.title.ilike(search_term) | 
                                     Goal.description.ilike(search_term))
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Goal, sort_by)))
        else:
            query = query.order_by(asc(getattr(Goal, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_by_user_id(
        db: Session, 
        user_id: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count goals by user ID with applied filters."""
        query = db.query(Goal).filter(Goal.user_id == user_id)
        
        # Apply filters
        if filters:
            if "status" in filters and filters["status"]:
                query = query.filter(Goal.status == filters["status"])
                
            if "goal_type" in filters and filters["goal_type"]:
                query = query.filter(Goal.goal_type == filters["goal_type"])
                
            if "is_public" in filters:
                query = query.filter(Goal.is_public == filters["is_public"])
                
            if "start_date_after" in filters and filters["start_date_after"]:
                query = query.filter(Goal.start_date >= filters["start_date_after"])
                
            if "deadline_before" in filters and filters["deadline_before"]:
                query = query.filter(Goal.deadline <= filters["deadline_before"])
                
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                query = query.filter(Goal.title.ilike(search_term) | 
                                    Goal.description.ilike(search_term))
                
        return query.count()

    @staticmethod
    def get_public_goals(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> List[Goal]:
        """Get public goals with filtering and sorting."""
        query = db.query(Goal).filter(Goal.is_public == True)
        
        # Apply filters
        if filters:
            if "user_id" in filters and filters["user_id"]:
                query = query.filter(Goal.user_id == filters["user_id"])
                
            if "status" in filters and filters["status"]:
                query = query.filter(Goal.status == filters["status"])
                
            if "goal_type" in filters and filters["goal_type"]:
                query = query.filter(Goal.goal_type == filters["goal_type"])
                
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                query = query.filter(Goal.title.ilike(search_term) | 
                                    Goal.description.ilike(search_term))
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Goal, sort_by)))
        else:
            query = query.order_by(asc(getattr(Goal, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_goals_with_approaching_deadline(
        db: Session, 
        days_threshold: int = 3
    ) -> List[Goal]:
        """Get goals with deadlines approaching within the specified days threshold."""
        threshold_date = datetime.now() + timedelta(days=days_threshold)
        
        return db.query(Goal).filter(
            Goal.status == GoalStatus.IN_PROGRESS,
            Goal.deadline <= threshold_date,
            Goal.deadline > datetime.now()
        ).all()

    @staticmethod
    def get_completion_percentage(db: Session, goal_id: int) -> float:
        """Calculate the completion percentage for a goal."""
        goal = db.query(Goal).filter(Goal.id == goal_id).first()
        if not goal or goal.target_value is None:
            return 0.0
        if not goal or goal.target_value is None or goal.target_value == 0:
            return 0.0
            
        latest_progress = db.query(Progress)\
            .filter(Progress.goal_id == goal_id)\
            .order_by(desc(Progress.date))\
            .first()
            
        if not latest_progress:
            return 0.0
            
        # Calculate percentage
        percentage = (latest_progress.value / goal.target_value) * 100
        
        # Cap at 100%
        return min(percentage, 100.0)