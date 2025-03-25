# File path: app/api/v1/endpoints/forums.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.dto.request.forum_dto import ForumCreateRequest, ForumUpdateRequest
from app.dto.response.forum_dto import ForumResponse, ForumDetailResponse, ForumListResponse
from app.services.forum_service import ForumService

router = APIRouter(prefix="/forums", tags=["Forums"])

@router.post("", response_model=ForumResponse, status_code=status.HTTP_201_CREATED)
def create_forum(
    forum_data: ForumCreateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Create a new forum (trainer or admin only)."""
    forum = ForumService.create_forum(db, forum_data, current_user)
    return forum

@router.get("", response_model=ForumListResponse)
def get_forums(
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(name|created_at)$"),
    sort_desc: bool = True,
    db: DbSession = Depends(get_db),
):
    """Get all forums with search, sorting, and pagination."""
    result = ForumService.get_forums(
        db, skip=skip, limit=limit, search=search, sort_by=sort_by, sort_desc=sort_desc
    )
    return result

@router.get("/my-forums", response_model=List[ForumResponse])
def get_my_forums(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get forums created by the current user."""
    forums = ForumService.get_user_forums(db, current_user.id, skip, limit)
    return forums

@router.get("/my-memberships", response_model=List[ForumResponse])
def get_my_memberships(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get forums that the current user is a member of."""
    forums = ForumService.get_user_memberships(db, current_user.id, skip, limit)
    return forums

@router.get("/{forum_id}", response_model=ForumDetailResponse)
def get_forum(
    forum_id: int,
    db: DbSession = Depends(get_db),
):
    """Get details of a specific forum."""
    forum = ForumService.get_forum(db, forum_id)
    return forum

@router.put("/{forum_id}", response_model=ForumResponse)
def update_forum(
    forum_id: int,
    forum_data: ForumUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Update a forum (creator, moderator, or admin only)."""
    forum = ForumService.update_forum(db, forum_id, forum_data, current_user)
    return forum

@router.delete("/{forum_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_forum(
    forum_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Delete a forum (creator or admin only)."""
    ForumService.delete_forum(db, forum_id, current_user)
    return None