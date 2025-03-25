# File path: app/api/v1/endpoints/likes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.like_service import LikeService

router = APIRouter(tags=["Likes"])

@router.post("/discussions/{discussion_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def like_discussion(
    discussion_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Like a discussion."""
    LikeService.like_discussion(db, discussion_id, current_user)
    return None

@router.delete("/discussions/{discussion_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_discussion(
   discussion_id: int,
   current_user: User = Depends(get_current_user),
   db: DbSession = Depends(get_db),
):
   """Unlike a discussion."""
   LikeService.unlike_discussion(db, discussion_id, current_user)
   return None

@router.post("/comments/{comment_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def like_comment(
   comment_id: int,
   current_user: User = Depends(get_current_user),
   db: DbSession = Depends(get_db),
):
   """Like a comment."""
   LikeService.like_comment(db, comment_id, current_user)
   return None

@router.delete("/comments/{comment_id}/like", status_code=status.HTTP_204_NO_CONTENT)
def unlike_comment(
   comment_id: int,
   current_user: User = Depends(get_current_user),
   db: DbSession = Depends(get_db),
):
   """Unlike a comment."""
   LikeService.unlike_comment(db, comment_id, current_user)
   return None