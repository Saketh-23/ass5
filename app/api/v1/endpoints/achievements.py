# app/api/v1/endpoints/achievements.py

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.models.user import User
from app.dto.request.achievement_dto import AchievementCreateRequest
from app.dto.response.achievement_dto import AchievementResponse, AchievementDetailResponse, AchievementListResponse
from app.services.achievement_service import AchievementService

router = APIRouter(prefix="/achievements", tags=["Achievements"])

@router.get("", response_model=AchievementListResponse)
def get_my_achievements(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("achieved_date", regex="^(title|achieved_date)$"),
    sort_desc: bool = True,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get achievements for the current user."""
    result = AchievementService.get_user_achievements(
        db, current_user.id, skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
    )
    
    return result

@router.get("/{achievement_id}", response_model=AchievementDetailResponse)
def get_achievement(
    achievement_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get details of a specific achievement."""
    achievement = AchievementService.get_achievement(db, achievement_id)
    
    # Check if achievement belongs to user
    if achievement.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this achievement",
        )
    
    result = AchievementService.get_achievement_with_details(db, achievement_id)
    return result

@router.post("", response_model=AchievementResponse, status_code=status.HTTP_201_CREATED)
def create_achievement(
    achievement_data: AchievementCreateRequest,
    current_user: User = Depends(get_current_admin_user),  # Only admins can create system achievements
    db: DbSession = Depends(get_db),
):
    """Create a system achievement (admin only)."""
    achievement = AchievementService.create_achievement(
        db=db,
        user_id=current_user.id,  # This will be overridden when awarded to users
        title=achievement_data.title,
        description=achievement_data.description,
        badge_url=achievement_data.badge_url,
        is_system=True
    )
    
    return achievement