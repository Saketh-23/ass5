from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User
from app.models.goal import Goal, GoalStatus
from app.dto.request.goal_dto import GoalCreateRequest, GoalUpdateRequest
from app.repositories.goal_repository import GoalRepository
from app.repositories.progress_repository import ProgressRepository
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType

class GoalService:
    @staticmethod
    def create_goal(db: Session, goal_data: GoalCreateRequest, user: User) -> Goal:
        """Create a new goal for a user."""
        # Create the goal
        goal = GoalRepository.create(
            db=db,
            user_id=user.id,
            title=goal_data.title,
            description=goal_data.description,
            goal_type=goal_data.goal_type,
            target_value=goal_data.target_value,
            start_date=goal_data.start_date,
            deadline=goal_data.deadline,
            status=GoalStatus.IN_PROGRESS,
            is_public=goal_data.is_public
        )
        
        # Create a notification for goal creation
        NotificationService.create_notification(
            db=db,
            user_id=user.id,
            title="Goal Created",
            content=f"You've created a new goal: {goal.title}",
            type=NotificationType.GOAL_REMINDER,
            goal_id=goal.id
        )
        
        return goal

    @staticmethod
    def get_goal(db: Session, goal_id: int) -> Goal:
        """Get a goal by ID."""
        goal = GoalRepository.get_by_id(db, goal_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Goal not found",
            )
        
        return goal

    @staticmethod
    def get_goal_with_details(db: Session, goal_id: int) -> Dict[str, Any]:
        """Get a goal by ID with additional details."""
        goal = GoalService.get_goal(db, goal_id)
        
        # Get progress entries
        progress_entries = ProgressRepository.get_by_goal_id(db, goal_id)
        
        # Get latest progress
        latest_progress = ProgressRepository.get_latest_progress(db, goal_id)
        
        # Calculate completion percentage
        completion_percentage = GoalRepository.get_completion_percentage(db, goal_id)
        
        # Calculate time remaining
        time_remaining = None
        if goal.deadline:
            time_remaining = (goal.deadline - datetime.now()).days
            if time_remaining < 0:
                time_remaining = 0
        
        # Determine if on track
        is_on_track = None
        if goal.deadline and latest_progress and goal.target_value:
            # Calculate elapsed time percentage
            total_time = (goal.deadline - goal.start_date).total_seconds()
            elapsed_time = (datetime.now() - goal.start_date).total_seconds()
            elapsed_percentage = (elapsed_time / total_time) * 100 if total_time > 0 else 100
            
            # On track if completion percentage >= elapsed time percentage
            is_on_track = completion_percentage >= elapsed_percentage
        
        # Build response
        result = {
            **goal.__dict__,
            "progress_history": progress_entries,
            "latest_progress": latest_progress.value if latest_progress else None,
            "completion_percentage": completion_percentage,
            "time_remaining": time_remaining,
            "is_on_track": is_on_track
        }
        
        return result

    @staticmethod
    def update_goal(
        db: Session, goal_id: int, goal_data: GoalUpdateRequest, user: User
    ) -> Goal:
        """Update a goal."""
        # Get the goal
        goal = GoalService.get_goal(db, goal_id)
        
        # Check if user owns the goal
        if goal.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this goal",
            )
        
        # Update the goal
        updated_goal = GoalRepository.update(
            db=db,
            goal=goal,
            title=goal_data.title,
            description=goal_data.description,
            goal_type=goal_data.goal_type,
            target_value=goal_data.target_value,
            deadline=goal_data.deadline,
            status=goal_data.status,
            is_public=goal_data.is_public,
        )
        
        # Check if goal was completed
        if goal_data.status == GoalStatus.COMPLETED and goal.status != GoalStatus.COMPLETED:
            # Trigger achievement check in achievement service
            from app.services.achievement_service import AchievementService
            AchievementService.check_goal_completion_achievements(db, user.id, goal_id)
            
            # Create a notification for goal completion
            NotificationService.create_notification(
                db=db,
                user_id=user.id,
                title="Goal Completed!",
                content=f"Congratulations! You've completed your goal: {goal.title}",
                type=NotificationType.GOAL_COMPLETED,
                goal_id=goal.id
            )
        
        return updated_goal

    @staticmethod
    def delete_goal(db: Session, goal_id: int, user: User) -> bool:
        """Delete a goal."""
        # Get the goal
        goal = GoalService.get_goal(db, goal_id)
        
        # Check if user owns the goal
        if goal.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this goal",
            )
        
        # Delete the goal
        return GoalRepository.delete(db, goal_id)

    @staticmethod
    def get_user_goals(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Get all goals for a user with pagination, filtering, and sorting."""
        goals = GoalRepository.get_by_user_id(
            db, user_id, skip=skip, limit=limit, filters=filters, sort_by=sort_by, sort_desc=sort_desc
        )
        
        # Enhance goals with completion percentages
        for goal in goals:
            goal.completion_percentage = GoalRepository.get_completion_percentage(db, goal.id)
        
        total = GoalRepository.count_by_user_id(db, user_id, filters=filters)
        
        return {
            "items": goals,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def get_public_goals(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Get public goals with pagination, filtering, and sorting."""
        goals = GoalRepository.get_public_goals(
            db, skip=skip, limit=limit, filters=filters, sort_by=sort_by, sort_desc=sort_desc
        )
        
        # Enhance goals with completion percentages
        for goal in goals:
            goal.completion_percentage = GoalRepository.get_completion_percentage(db, goal.id)
        
        # Count would require a separate query, but we'll just use the length for now
        total = len(goals)
        
        return {
            "items": goals,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def check_approaching_deadlines(db: Session):
        """Check for goals with approaching deadlines and send notifications."""
        approaching_goals = GoalRepository.get_goals_with_approaching_deadline(db)
        
        for goal in approaching_goals:
            days_remaining = (goal.deadline - datetime.now()).days
            
            # Create a notification for approaching deadline
            NotificationService.create_notification(
                db=db,
                user_id=goal.user_id,
                title="Goal Deadline Approaching",
                content=f"Your goal '{goal.title}' is due in {days_remaining} days!",
                type=NotificationType.GOAL_DEADLINE,
                goal_id=goal.id
            )