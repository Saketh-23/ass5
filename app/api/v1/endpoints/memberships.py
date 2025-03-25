# File path: app/api/v1/endpoints/memberships.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.forum_membership import MembershipStatus, MembershipRole
from app.dto.request.membership_dto import MembershipUpdateRequest
from app.dto.response.membership_dto import MembershipResponse, MembershipDetailResponse, MembershipListResponse
from app.services.membership_service import MembershipService

router = APIRouter(tags=["Forum Memberships"])

@router.post("/forums/{forum_id}/join", response_model=MembershipResponse, status_code=status.HTTP_201_CREATED)
def join_forum(
    forum_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Join a forum."""
    membership = MembershipService.join_forum(db, forum_id, current_user)
    return membership

@router.delete("/forums/{forum_id}/leave", status_code=status.HTTP_204_NO_CONTENT)
def leave_forum(
    forum_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Leave a forum."""
    MembershipService.leave_forum(db, forum_id, current_user)
    return None

@router.get("/forums/{forum_id}/members", response_model=MembershipListResponse)
def get_forum_members(
    forum_id: int,
    status: Optional[MembershipStatus] = MembershipStatus.ACTIVE,
    role: Optional[MembershipRole] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: DbSession = Depends(get_db),
):
    """Get all members of a forum."""
    result = MembershipService.get_forum_members(
        db, forum_id, skip=skip, limit=limit, status=status, role=role
    )
    return result

@router.put("/forums/{forum_id}/members/{user_id}", response_model=MembershipResponse)
def update_membership(
    forum_id: int,
    user_id: int,
    membership_data: MembershipUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Update a forum membership (forum creator, moderator, or admin only)."""
    membership = MembershipService.update_membership(db, forum_id, user_id, membership_data, current_user)
    return membership