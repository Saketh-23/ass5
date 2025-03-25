# File path: app/services/like_service.py
from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.models.like import Like, LikeTargetType
from app.models.user import User, UserRole
from app.repositories.like_repository import LikeRepository
from app.repositories.discussion_repository import DiscussionRepository
from app.repositories.comment_repository import CommentRepository
from app.repositories.membership_repository import MembershipRepository

class LikeService:
    @staticmethod
    def like_discussion(db: DbSession, discussion_id: int, user: User) -> Like:
        """Like a discussion."""
        # Check if discussion exists
        discussion = DiscussionRepository.get_by_id(db, discussion_id)
        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Discussion with ID {discussion_id} not found",
            )
        
        # Check if user is a member of the forum
        is_member = MembershipRepository.is_member(db, discussion.forum_id, user.id)
        if not is_member and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of the forum to like discussions",
            )
        
        # Check if user already liked the discussion
        existing_like = LikeRepository.get_discussion_like(db, discussion_id, user.id)
        if existing_like:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already liked this discussion",
            )
        
        # Create the like
        return LikeRepository.create(
            db=db,
            user_id=user.id,
            target_type=LikeTargetType.DISCUSSION,
            discussion_id=discussion_id,
            comment_id=None,
        )

    @staticmethod
    def unlike_discussion(db: DbSession, discussion_id: int, user: User) -> bool:
        """Unlike a discussion."""
        # Check if discussion exists
        discussion = DiscussionRepository.get_by_id(db, discussion_id)
        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Discussion with ID {discussion_id} not found",
            )
        
        # Check if user liked the discussion
        existing_like = LikeRepository.get_discussion_like(db, discussion_id, user.id)
        if not existing_like:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You haven't liked this discussion",
            )
        
        # Delete the like
        return LikeRepository.delete(db, existing_like.id)

    @staticmethod
    def like_comment(db: DbSession, comment_id: int, user: User) -> Like:
        """Like a comment."""
        # Check if comment exists
        comment = CommentRepository.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment with ID {comment_id} not found",
            )
        
        # Get the discussion to check forum permissions
        discussion = DiscussionRepository.get_by_id(db, comment.discussion_id)
        
        # Check if user is a member of the forum
        is_member = MembershipRepository.is_member(db, discussion.forum_id, user.id)
        if not is_member and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of the forum to like comments",
            )
        
        # Check if user already liked the comment
        existing_like = LikeRepository.get_comment_like(db, comment_id, user.id)
        if existing_like:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already liked this comment",
            )
        
        # Create the like
        return LikeRepository.create(
            db=db,
            user_id=user.id,
            target_type=LikeTargetType.COMMENT,
            discussion_id=None,
            comment_id=comment_id,
        )

    @staticmethod
    def unlike_comment(db: DbSession, comment_id: int, user: User) -> bool:
        """Unlike a comment."""
        # Check if comment exists
        comment = CommentRepository.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Comment with ID {comment_id} not found",
            )
        
        # Check if user liked the comment
        existing_like = LikeRepository.get_comment_like(db, comment_id, user.id)
        if not existing_like:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You haven't liked this comment",
            )
        
        # Delete the like
        return LikeRepository.delete(db, existing_like.id)