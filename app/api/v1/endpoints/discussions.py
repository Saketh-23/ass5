# File path: app/api/v1/endpoints/discussions.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.dto.request.discussion_dto import DiscussionCreateRequest, DiscussionUpdateRequest
from app.dto.response.discussion_dto import DiscussionResponse, DiscussionDetailResponse, DiscussionListResponse
from app.services.discussion_service import DiscussionService

router = APIRouter(tags=["Discussions"])

@router.post("/forums/{forum_id}/discussions", response_model=DiscussionResponse, status_code=status.HTTP_201_CREATED)
def create_discussion(
    forum_id: int,
    discussion_data: DiscussionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Create a new discussion in a forum."""
    # Ensure forum_id in path matches the one in request body
    if discussion_data.forum_id != forum_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Forum ID in path does not match forum ID in request body",
        )
    
    discussion = DiscussionService.create_discussion(db, discussion_data, current_user)
    return discussion

@router.get("/forums/{forum_id}/discussions", response_model=DiscussionListResponse)
def get_forum_discussions(
    forum_id: int,
    search: Optional[str] = None,
    is_pinned: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(title|created_at)$"),
    sort_desc: bool = True,
    db: DbSession = Depends(get_db),
):
    """Get all discussions in a forum."""
    result = DiscussionService.get_forum_discussions(
        db, forum_id, skip=skip, limit=limit, search=search, 
        is_pinned=is_pinned, sort_by=sort_by, sort_desc=sort_desc
    )
    return result

@router.get("/discussions/{discussion_id}", response_model=DiscussionDetailResponse)
def get_discussion(
    discussion_id: int,
    db: DbSession = Depends(get_db),
):
    """Get details of a specific discussion."""
    discussion = DiscussionService.get_discussion(db, discussion_id)
    return discussion

@router.put("/discussions/{discussion_id}", response_model=DiscussionResponse)
def update_discussion(
    discussion_id: int,
    discussion_data: DiscussionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Update a discussion."""
    discussion = DiscussionService.update_discussion(db, discussion_id, discussion_data, current_user)
    return discussion

@router.delete("/discussions/{discussion_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_discussion(
    discussion_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Delete a discussion."""
    DiscussionService.delete_discussion(db, discussion_id, current_user)
    return None

@router.put("/discussions/{discussion_id}/pin", response_model=DiscussionResponse)
def pin_discussion(
    discussion_id: int,
    pin: bool = True,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Pin or unpin a discussion (moderator or admin only)."""
    discussion = DiscussionService.pin_discussion(db, discussion_id, pin, current_user)
    return discussion

@router.put("/discussions/{discussion_id}/lock", response_model=DiscussionResponse)
def lock_discussion(
    discussion_id: int,
    lock: bool = True,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Lock or unlock a discussion (moderator or admin only)."""
    discussion = DiscussionService.lock_discussion(db, discussion_id, lock, current_user)
    return discussion

@router.get("/users/me/discussions", response_model=List[DiscussionResponse])
def get_my_discussions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get discussions created by the current user."""
    discussions = DiscussionService.get_user_discussions(db, current_user.id, skip, limit)
    return discussions