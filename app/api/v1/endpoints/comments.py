# File path: app/api/v1/endpoints/comments.py
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.dto.request.comment_dto import CommentCreateRequest, CommentUpdateRequest
from app.dto.response.comment_dto import CommentResponse, CommentDetailResponse, CommentListResponse
from app.services.comment_service import CommentService

router = APIRouter(tags=["Comments"])

@router.post("/discussions/{discussion_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    discussion_id: int,
    comment_data: CommentCreateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Create a new comment or reply."""
    # Ensure discussion_id in path matches the one in request body
    if comment_data.discussion_id != discussion_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discussion ID in path does not match discussion ID in request body",
        )
    
    comment = CommentService.create_comment(db, comment_data, current_user)
    return comment

@router.get("/discussions/{discussion_id}/comments", response_model=CommentListResponse)
def get_discussion_comments(
    discussion_id: int,
    parent_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at)$"),
    sort_desc: bool = True,
    current_user: Optional[User] = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get comments for a discussion."""
    result = CommentService.get_discussion_comments(
        db, discussion_id, 
        user_id=current_user.id if current_user else None,
        parent_id=parent_id, 
        skip=skip, limit=limit, 
        sort_by=sort_by, sort_desc=sort_desc
    )
    return result

@router.get("/comments/{comment_id}", response_model=CommentDetailResponse)
def get_comment(
    comment_id: int,
    current_user: Optional[User] = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get a specific comment."""
    comment = CommentService.get_comment(
        db, comment_id, 
        user_id=current_user.id if current_user else None
    )
    return comment

@router.put("/comments/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: int,
    comment_data: CommentUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Update a comment."""
    comment = CommentService.update_comment(db, comment_id, comment_data, current_user)
    return comment

@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Delete a comment."""
    CommentService.delete_comment(db, comment_id, current_user)
    return None