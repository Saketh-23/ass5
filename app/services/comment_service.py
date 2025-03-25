# File path: app/services/comment_service.py
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.models.comment import Comment
from app.models.user import User, UserRole
from app.dto.request.comment_dto import CommentCreateRequest, CommentUpdateRequest
from app.repositories.comment_repository import CommentRepository
from app.repositories.discussion_repository import DiscussionRepository
from app.repositories.membership_repository import MembershipRepository

class CommentService:
    @staticmethod
    def create_comment(db: DbSession, comment_data: CommentCreateRequest, user: User) -> Comment:
        """Create a new comment."""
        # Check if discussion exists
        discussion = DiscussionRepository.get_by_id(db, comment_data.discussion_id)
        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Discussion with ID {comment_data.discussion_id} not found",
            )
        
        # Check if discussion is locked
        if discussion.is_locked:
            # Allow admins and moderators to comment on locked discussions
            is_admin = user.role == UserRole.ADMIN
            is_moderator = MembershipRepository.is_moderator(db, discussion.forum_id, user.id)
            
            if not (is_admin or is_moderator):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot comment on a locked discussion",
                )
        
        # Check if user is a member of the forum
        is_member = MembershipRepository.is_member(db, discussion.forum_id, user.id)
        if not is_member and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of the forum to comment",
            )
        
        # If it's a reply, check if parent comment exists and belongs to the same discussion
        if comment_data.parent_id:
            parent_comment = CommentRepository.get_by_id(db, comment_data.parent_id)
            if not parent_comment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent comment with ID {comment_data.parent_id} not found",
                )
            
            if parent_comment.discussion_id != comment_data.discussion_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Parent comment does not belong to the specified discussion",
                )
        
        # Create the comment
        return CommentRepository.create(
            db=db,
            discussion_id=comment_data.discussion_id,
            user_id=user.id,
            content=comment_data.content,
            parent_id=comment_data.parent_id,
        )

    @staticmethod
    def get_comment(db: DbSession, comment_id: int, user_id: Optional[int] = None) -> Comment:
        """Get a comment by ID with like information."""
        comment = CommentRepository.get_by_id(db, comment_id)
        if not comment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        
        # Add like count
        comment.like_count = CommentRepository.get_like_count(db, comment_id)
        
        # Add is_liked_by_user flag if user_id is provided
        if user_id:
            comment.is_liked_by_user = CommentRepository.is_liked_by_user(db, comment_id, user_id)
        
        return comment

    @staticmethod
    def update_comment(
        db: DbSession, comment_id: int, comment_data: CommentUpdateRequest, user: User
    ) -> Comment:
        """Update a comment."""
        # Get the comment
        comment = CommentService.get_comment(db, comment_id)
        
        # Check if user is the creator or has special permissions
        if comment.user_id != user.id:
            # Get the discussion to check forum permissions
            discussion = DiscussionRepository.get_by_id(db, comment.discussion_id)
            
            is_admin = user.role == UserRole.ADMIN
            is_moderator = MembershipRepository.is_moderator(db, discussion.forum_id, user.id)
            
            if not (is_admin or is_moderator):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the creator, moderators, or admins can update this comment",
                )
        
        # Update the comment
        updated_comment = CommentRepository.update(
            db=db,
            comment=comment,
            content=comment_data.content,
        )
        
        # Add like count and is_liked_by_user flag
        updated_comment.like_count = CommentRepository.get_like_count(db, comment_id)
        updated_comment.is_liked_by_user = CommentRepository.is_liked_by_user(db, comment_id, user.id)
        
        return updated_comment

    @staticmethod
    def delete_comment(db: DbSession, comment_id: int, user: User) -> bool:
        """Delete a comment."""
        # Get the comment
        comment = CommentService.get_comment(db, comment_id)
        
        # Check if user is the creator or has special permissions
        if comment.user_id != user.id:
            # Get the discussion to check forum permissions
            discussion = DiscussionRepository.get_by_id(db, comment.discussion_id)
            
            is_admin = user.role == UserRole.ADMIN
            is_moderator = MembershipRepository.is_moderator(db, discussion.forum_id, user.id)
            
            if not (is_admin or is_moderator):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the creator, moderators, or admins can delete this comment",
                )
        
        # Delete the comment
        return CommentRepository.delete(db, comment_id)

    @staticmethod
    def get_discussion_comments(
        db: DbSession,
        discussion_id: int,
        user_id: Optional[int] = None,
        parent_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Get comments for a discussion with pagination and sorting."""
        # Check if discussion exists
        discussion = DiscussionRepository.get_by_id(db, discussion_id)
        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Discussion with ID {discussion_id} not found",
            )
        
        # Get comments
        comments = CommentRepository.get_by_discussion_id(
            db, discussion_id, parent_id, skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
        )
        
        # Get total count
        total = CommentRepository.count_by_discussion_id(db, discussion_id, parent_id)
        
        # Enrich comments with additional information
        for comment in comments:
            # Add like count
            comment.like_count = CommentRepository.get_like_count(db, comment.id)
            
            # Add is_liked_by_user flag if user_id is provided
            if user_id:
                comment.is_liked_by_user = CommentRepository.is_liked_by_user(db, comment.id, user_id)
            
            # Get replies for top-level comments
            if parent_id is None:
                replies = CommentRepository.get_replies(db, comment.id)
                
                # Enrich replies with like information
                for reply in replies:
                    reply.like_count = CommentRepository.get_like_count(db, reply.id)
                    if user_id:
                        reply.is_liked_by_user = CommentRepository.is_liked_by_user(db, reply.id, user_id)
                
                comment.replies = replies
        
        return {
            "items": comments,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }