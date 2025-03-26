# app/services/progress_service.py
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.progress import Progress
from app.models.user import User
from app.models.goal import Goal, GoalStatus
from app.dto.request.progress_dto import ProgressCreateRequest, ProgressUpdateRequest
from app.repositories.goal_repository import GoalRepository
from app.repositories.progress_repository import ProgressRepository
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType

class ProgressService:
    @staticmethod
    def create_progress(db: Session, progress_data: ProgressCreateRequest, user: User) -> Progress:
        """Create a new progress entry for a goal."""
    # Get the goal
        goal = GoalRepository.get_by_id(db, progress_data.goal_id)
        if not goal:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Goal with ID {progress_data.goal_id} not found",
        )
    
    # Check if user owns the goal
        if goal.user_id != user.id:
            raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to add progress to this goal",
            )
    
    # Check if goal is still in progress
        if goal.status != GoalStatus.IN_PROGRESS:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot add progress to a {goal.status} goal",
        )
    
    # Create the progress entry
        progress = ProgressRepository.create(
        db=db,
        goal_id=progress_data.goal_id,
        date=progress_data.date,
        value=progress_data.value,
        notes=progress_data.notes
        )
    
    # Check if goal has been reached
        if goal.target_value is not None:
        # For goals where higher values mean progress
            if progress_data.value >= goal.target_value:
            # Update goal status to completed
                GoalRepository.update(db, goal, status=GoalStatus.COMPLETED)
            
            # Create a notification for goal completion
                NotificationService.create_notification(
                db=db,
                user_id=user.id,
                title="Goal Achieved!",
                content=f"Congratulations! You've reached your target for '{goal.title}'",
                type=NotificationType.GOAL_COMPLETED,
                goal_id=goal.id
            )
    
    # Calculate progress percentage for response
        completion_percentage = GoalRepository.get_completion_percentage(db, goal.id)
    
    # Check for progress milestone
        previous_percentage = 0
        previous_progress = ProgressRepository.get_by_goal_id(db, goal.id, limit=2, sort_desc=True)
        if len(previous_progress) > 1:
        # If this isn't the first progress entry, calculate previous percentage
            if goal.target_value and goal.target_value > 0:
                previous_percentage = (previous_progress[1].value / goal.target_value) * 100
    
    # Check for milestones (25%, 50%, 75%)
        milestones = [25, 50, 75]
        for milestone in milestones:
            if previous_percentage < milestone and completion_percentage >= milestone:
            # Create milestone notification
                NotificationService.create_notification(
                db=db,
                user_id=user.id,
                title=f"{milestone}% Milestone Reached!",
                content=f"You're {milestone}% of the way to completing '{goal.title}'",
                type=NotificationType.PROGRESS_MILESTONE,
                goal_id=goal.id
            )
    
    # Set additional attributes on progress object (will be accessible in the response)
        progress.goal_title = goal.title
        progress.target_value = goal.target_value
        progress.percentage = completion_percentage
    
        return progress

    @staticmethod
    def get_progress(db: Session, progress_id: int) -> Dict[str, Any]:
        """Get a progress entry by ID with additional details."""
        progress = ProgressRepository.get_by_id(db, progress_id)
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress entry not found",
            )
        
        # Get the goal for additional info
        goal = GoalRepository.get_by_id(db, progress.goal_id)
        
        # Calculate percentage if goal has a target value
        percentage = None
        if goal and goal.target_value:
            percentage = (progress.value / goal.target_value) * 100
            # Cap at 100%
            percentage = min(percentage, 100.0)
        
        # Build enhanced response
        return {
            **progress.__dict__,
            "goal_title": goal.title if goal else None,
            "target_value": goal.target_value if goal else None,
            "percentage": percentage
        }

    @staticmethod
    def update_progress(
        db: Session, progress_id: int, progress_data: ProgressUpdateRequest, user: User
    ) -> Dict[str, Any]:
        """Update a progress entry."""
        # Get the progress entry
        progress = ProgressRepository.get_by_id(db, progress_id)
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress entry not found",
            )
        
        # Get the goal to check ownership
        goal = GoalRepository.get_by_id(db, progress.goal_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated goal not found",
            )
        
        # Check if user owns the goal
        if goal.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this progress entry",
            )
        
        # Update the progress entry
        updated_progress = ProgressRepository.update(
            db=db,
            progress=progress,
            date=progress_data.date,
            value=progress_data.value,
            notes=progress_data.notes
        )
        
        # Check if goal has been reached with updated progress
        if goal.target_value is not None and progress_data.value is not None:
            if progress_data.value >= goal.target_value and goal.status == GoalStatus.IN_PROGRESS:
                # Update goal status to completed
                GoalRepository.update(db, goal, status=GoalStatus.COMPLETED)
                
                # Create a notification for goal completion
                NotificationService.create_notification(
                    db=db,
                    user_id=user.id,
                    title="Goal Achieved!",
                    content=f"Congratulations! You've reached your target for '{goal.title}'",
                    type=NotificationType.GOAL_COMPLETED,
                    goal_id=goal.id
                )
        
        # Calculate percentage for response
        percentage = None
        if goal.target_value:
            percentage = (updated_progress.value / goal.target_value) * 100
            # Cap at 100%
            percentage = min(percentage, 100.0)
        
        # Build enhanced response
        return {
            **updated_progress.__dict__,
            "goal_title": goal.title,
            "target_value": goal.target_value,
            "percentage": percentage
        }

    @staticmethod
    def delete_progress(db: Session, progress_id: int, user: User) -> bool:
        """Delete a progress entry."""
        # Get the progress entry
        progress = ProgressRepository.get_by_id(db, progress_id)
        if not progress:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Progress entry not found",
            )
        
        # Get the goal to check ownership
        goal = GoalRepository.get_by_id(db, progress.goal_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Associated goal not found",
            )
        
        # Check if user owns the goal
        if goal.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this progress entry",
            )
        
        # Delete the progress entry
        return ProgressRepository.delete(db, progress_id)

    @staticmethod
    def get_goal_progress(
        db: Session,
        goal_id: int,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "date",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Get all progress entries for a goal with pagination and sorting."""
        # Check if goal exists
        goal = GoalRepository.get_by_id(db, goal_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Goal with ID {goal_id} not found",
            )
        
        progress_entries = ProgressRepository.get_by_goal_id(
            db, goal_id, skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
        )
        
        total = ProgressRepository.count_by_goal_id(db, goal_id)
        
        # Enhance entries with percentage if goal has a target value
        if goal.target_value:
            for entry in progress_entries:
                entry.percentage = (entry.value / goal.target_value) * 100
                # Cap at 100%
                entry.percentage = min(entry.percentage, 100.0)
        
        return {
            "items": progress_entries,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }