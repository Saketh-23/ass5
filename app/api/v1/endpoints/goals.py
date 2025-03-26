# app/api/v1/endpoints/goals.py
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.goal import GoalStatus, GoalType
from app.dto.request.goal_dto import GoalCreateRequest, GoalUpdateRequest
from app.dto.response.goal_dto import GoalResponse, GoalDetailResponse, GoalListResponse
from app.services.goal_service import GoalService

router = APIRouter(prefix="/goals", tags=["Goals"])

@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
def create_goal(
    goal_data: GoalCreateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Create a new goal."""
    goal = GoalService.create_goal(db, goal_data, current_user)
    return goal

@router.get("", response_model=GoalListResponse)
def get_my_goals(
    status: Optional[GoalStatus] = None,
    goal_type: Optional[GoalType] = None,
    is_public: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(title|start_date|deadline|created_at)$"),
    sort_desc: bool = True,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get goals for the current user with filtering and sorting."""
    filters = {}
    
    if status:
        filters["status"] = status
        
    if goal_type:
        filters["goal_type"] = goal_type
        
    if is_public is not None:
        filters["is_public"] = is_public
        
    if search:
        filters["search"] = search
    
    result = GoalService.get_user_goals(
        db, current_user.id, skip=skip, limit=limit, filters=filters, sort_by=sort_by, sort_desc=sort_desc
    )
    
    return result

@router.get("/public", response_model=GoalListResponse)
def get_public_goals(
    user_id: Optional[int] = None,
    status: Optional[GoalStatus] = None,
    goal_type: Optional[GoalType] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(title|start_date|deadline|created_at)$"),
    sort_desc: bool = True,
    db: DbSession = Depends(get_db),
):
    """Get public goals with filtering and sorting."""
    filters = {}
    
    if user_id:
        filters["user_id"] = user_id
        
    if status:
        filters["status"] = status
        
    if goal_type:
        filters["goal_type"] = goal_type
        
    if search:
        filters["search"] = search
    
    result = GoalService.get_public_goals(
        db, skip=skip, limit=limit, filters=filters, sort_by=sort_by, sort_desc=sort_desc
    )
    
    return result

@router.get("/{goal_id}", response_model=GoalDetailResponse)
def get_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get details of a specific goal."""
    # Get goal and check if user has access
    goal = GoalService.get_goal(db, goal_id)
    
    if goal.user_id != current_user.id and not goal.is_public:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this goal",
        )
    
    result = GoalService.get_goal_with_details(db, goal_id)
    return result

@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: int,
    goal_data: GoalUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Update a goal."""
    goal = GoalService.update_goal(db, goal_id, goal_data, current_user)
    return goal

@router.delete("/{goal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Delete a goal."""
    GoalService.delete_goal(db, goal_id, current_user)
    return None

@router.get("/{goal_id}/assessment", response_model=Dict[str, Any])
def get_goal_assessment(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get progress assessment for a goal."""
    from app.services.progress_assessment_service import ProgressAssessmentService
    
    assessment = ProgressAssessmentService.assess_goal_progress(db, goal_id, current_user.id)
    return assessment

@router.get("/{goal_id}/prediction", response_model=Dict[str, Any])
def get_goal_prediction(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get completion prediction for a goal."""
    from app.services.progress_assessment_service import ProgressAssessmentService
    
    prediction = ProgressAssessmentService.predict_completion(db, goal_id, current_user.id)
    return prediction