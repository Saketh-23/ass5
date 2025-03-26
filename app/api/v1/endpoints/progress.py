# app/api/v1/endpoints/progress.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.dto.request.progress_dto import ProgressCreateRequest, ProgressUpdateRequest
from app.dto.response.progress_dto import ProgressResponse, ProgressDetailResponse, ProgressListResponse
from app.services.progress_service import ProgressService
from app.services.goal_service import GoalService

router = APIRouter(tags=["Progress"])

@router.post("/goals/{goal_id}/progress", response_model=ProgressDetailResponse, status_code=status.HTTP_201_CREATED)
def create_progress(
    goal_id: int,
    progress_data: ProgressCreateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Record progress for a goal."""
    # Ensure goal_id in path matches the one in request body
    if progress_data.goal_id != goal_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Goal ID in path does not match goal ID in request body",
        )
    
    progress = ProgressService.create_progress(db, progress_data, current_user)
    
    # Check for streak achievements
    from app.services.achievement_service import AchievementService
    AchievementService.check_progress_streak_achievements(db, current_user.id, goal_id)
    
    return progress

@router.get("/goals/{goal_id}/progress", response_model=ProgressListResponse)
def get_goal_progress(
    goal_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("date", regex="^(date|value|created_at)$"),
    sort_desc: bool = True,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get progress entries for a goal."""
    # Check if user has access to the goal
    goal = GoalService.get_goal(db, goal_id)
    
    if goal.user_id != current_user.id and not goal.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view progress for this goal",
        )
    
    result = ProgressService.get_goal_progress(
        db, goal_id, skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
    )
    
    return result

@router.get("/progress/{progress_id}", response_model=ProgressDetailResponse)
def get_progress(
    progress_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get details of a specific progress entry."""
    progress = ProgressService.get_progress(db, progress_id)
    
    # Check if user has access to the progress entry
    goal = GoalService.get_goal(db, progress["goal_id"])
    
    if goal.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this progress entry",
        )
    
    return progress

@router.put("/progress/{progress_id}", response_model=ProgressDetailResponse)
def update_progress(
    progress_id: int,
    progress_data: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Update a progress entry."""
    progress = ProgressService.update_progress(db, progress_id, progress_data, current_user)
    return progress

@router.delete("/progress/{progress_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_progress(
    progress_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Delete a progress entry."""
    ProgressService.delete_progress(db, progress_id, current_user)
    return None