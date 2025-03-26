# app/services/achievement_service.py

from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models.user import User
from app.models.goal import Goal, GoalStatus, GoalType
from app.models.achievement import Achievement
from app.repositories.goal_repository import GoalRepository
from app.repositories.achievement_repository import AchievementRepository
from app.repositories.progress_repository import ProgressRepository
from app.services.notification_service import NotificationService
from app.models.notification import NotificationType

class AchievementService:
    # Define achievement types
    ACHIEVEMENT_FIRST_GOAL = "First Goal Completed"
    ACHIEVEMENT_CONSISTENCY = "Consistency Champion"
    ACHIEVEMENT_STREAK = "Progress Streak"
    ACHIEVEMENT_AHEAD = "Ahead of Schedule"
    ACHIEVEMENT_MULTIPLE = "Multiple Goals Master"
    ACHIEVEMENT_CATEGORY = "Category Expert"
    
    @staticmethod
    def get_achievement(db: Session, achievement_id: int) -> Achievement:
        """Get an achievement by ID."""
        achievement = AchievementRepository.get_by_id(db, achievement_id)
        if not achievement:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Achievement not found",
            )
        
        return achievement

    @staticmethod
    def get_achievement_with_details(db: Session, achievement_id: int) -> Dict[str, Any]:
        """Get an achievement by ID with additional details."""
        achievement = AchievementService.get_achievement(db, achievement_id)
        
        # Get the goal if it exists
        goal_title = None
        if achievement.goal_id:
            goal = GoalRepository.get_by_id(db, achievement.goal_id)
            if goal:
                goal_title = goal.title
        
        # Build enhanced response
        result = {
            **achievement.__dict__,
            "goal_title": goal_title
        }
        
        return result

    @staticmethod
    def get_user_achievements(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "achieved_date",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Get all achievements for a user with pagination and sorting."""
        achievements = AchievementRepository.get_by_user_id(
            db, user_id, skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
        )
        
        total = AchievementRepository.count_by_user_id(db, user_id)
        
        return {
            "items": achievements,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def create_achievement(
        db: Session,
        user_id: int,
        title: str,
        description: str,
        goal_id: Optional[int] = None,
        badge_url: Optional[str] = None,
        is_system: bool = True
    ) -> Achievement:
        """Create a new achievement for a user."""
        # Check if achievement already exists
        if AchievementRepository.check_achievement_exists(db, user_id, title):
            return None  # User already has this achievement
        
        # Create the achievement
        achievement = AchievementRepository.create(
            db=db,
            user_id=user_id,
            goal_id=goal_id,
            title=title,
            description=description,
            badge_url=badge_url,
            is_system=is_system,
            achieved_date=datetime.now()
        )
        
        # Create a notification for the achievement
        NotificationService.create_notification(
            db=db,
            user_id=user_id,
            title="Achievement Unlocked!",
            content=f"Congratulations! You've earned the '{title}' achievement",
            type=NotificationType.ACHIEVEMENT_UNLOCKED,
            achievement_id=achievement.id
        )
        
        return achievement

    @staticmethod
    def check_goal_completion_achievements(db: Session, user_id: int, goal_id: int) -> None:
        """Check and award achievements when a goal is completed."""
        # Get the completed goal
        goal = GoalRepository.get_by_id(db, goal_id)
        if not goal or goal.status != GoalStatus.COMPLETED:
            return
        
        # Get all user's completed goals
        completed_goals = GoalRepository.get_by_user_id(
            db, 
            user_id, 
            filters={"status": GoalStatus.COMPLETED}
        )
        
        # First goal achievement
        if len(completed_goals) == 1:
            AchievementService.create_achievement(
                db=db,
                user_id=user_id,
                title=AchievementService.ACHIEVEMENT_FIRST_GOAL,
                description="Completed your first goal. The journey of a thousand miles begins with a single step!",
                goal_id=goal_id,
                badge_url="/badges/first_goal.png"
            )
        
        # Multiple goals achievement
        if len(completed_goals) == 5:
            AchievementService.create_achievement(
                db=db,
                user_id=user_id,
                title=AchievementService.ACHIEVEMENT_MULTIPLE,
                description="Completed 5 goals. You're on a roll!",
                badge_url="/badges/multiple_goals.png"
            )
        elif len(completed_goals) == 10:
            AchievementService.create_achievement(
                db=db,
                user_id=user_id,
                title="Goal Master",
                description="Completed 10 goals. You're a master of achievement!",
                badge_url="/badges/goal_master.png"
            )
        
        # Category expert achievements
        category_counts = {}
        for completed_goal in completed_goals:
            category = completed_goal.goal_type
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
        
        # Check if user has completed 3 goals in any category
        for category, count in category_counts.items():
            if count == 3:
                AchievementService.create_achievement(
                    db=db,
                    user_id=user_id,
                    title=f"{category.value} Expert",
                    description=f"Completed 3 goals in the {category.value} category. You're becoming an expert!",
                    badge_url=f"/badges/{category.value.lower()}_expert.png"
                )
        
        # Ahead of schedule achievement
        if goal.deadline:
            days_early = (goal.deadline - datetime.now()).days
            if days_early > 3:  # Completed at least 3 days ahead of schedule
                AchievementService.create_achievement(
                    db=db,
                    user_id=user_id,
                    title=AchievementService.ACHIEVEMENT_AHEAD,
                    description="Completed a goal well ahead of schedule. Great planning and execution!",
                    goal_id=goal_id,
                    badge_url="/badges/ahead_of_schedule.png"
                )
        
        # Consistency achievement - check if progress was added regularly
        progress_entries = ProgressRepository.get_by_goal_id(db, goal_id)
        if len(progress_entries) >= 5:  # Need at least 5 entries to check consistency
            # Sort by date
            progress_entries.sort(key=lambda x: x.date)
            
            # Check intervals between updates
            intervals = []
            for i in range(1, len(progress_entries)):
                interval = (progress_entries[i].date - progress_entries[i-1].date).days
                intervals.append(interval)
            
            # Calculate average and standard deviation
            avg_interval = sum(intervals) / len(intervals)
            std_dev = (sum((x - avg_interval) ** 2 for x in intervals) / len(intervals)) ** 0.5
            
            # If standard deviation is low, progress was consistent
            if std_dev <= 1 and avg_interval <= 3:  # Consistent updates at least every 3 days
                AchievementService.create_achievement(
                    db=db,
                    user_id=user_id,
                    title=AchievementService.ACHIEVEMENT_CONSISTENCY,
                    description="Consistently tracked progress toward your goal. Consistency is key to success!",
                    goal_id=goal_id,
                    badge_url="/badges/consistency.png"
                )

    @staticmethod
    def check_progress_streak_achievements(db: Session, user_id: int, goal_id: int) -> None:
        """Check and award achievements for consistent progress streaks."""
        progress_entries = ProgressRepository.get_by_goal_id(db, goal_id, sort_by="date", sort_desc=False)
        
        # Need at least 7 entries to check for a streak
        if len(progress_entries) < 7:
            return
        
        # Check for a 7-day streak
        current_streak = 1
        max_streak = 1
        
        for i in range(1, len(progress_entries)):
            current_entry_date = progress_entries[i].date.date()
            prev_entry_date = progress_entries[i-1].date.date()
            
            # Check if entries are on consecutive days
            if (current_entry_date - prev_entry_date).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        
        # Award achievement for 7-day streak
        if max_streak >= 7 and not AchievementRepository.check_achievement_exists(db, user_id, AchievementService.ACHIEVEMENT_STREAK):
            AchievementService.create_achievement(
                db=db,
                user_id=user_id,
                title=AchievementService.ACHIEVEMENT_STREAK,
                description="Recorded progress for 7 consecutive days. What fantastic dedication!",
                goal_id=goal_id,
                badge_url="/badges/progress_streak.png"
            )