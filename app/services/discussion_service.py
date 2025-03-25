# File path: app/services/discussion_service.py
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.models.discussion import Discussion
from app.models.user import User, UserRole
from app.dto.request.discussion_dto import DiscussionCreateRequest, DiscussionUpdateRequest
from app.repositories.comment_repository import CommentRepository
from app.repositories.forum_repository import ForumRepository
from app.repositories.membership_repository import MembershipRepository
from app.repositories.discussion_repository import DiscussionRepository

class DiscussionService:
    @staticmethod
    def create_discussion(db: DbSession, discussion_data: DiscussionCreateRequest, user: User) -> Discussion:
        """Create a new discussion."""
        # Check if forum exists
        forum = ForumRepository.get_by_id(db, discussion_data.forum_id)
        if not forum:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forum with ID {discussion_data.forum_id} not found",
            )
        
        # Check if forum is active
        if not forum.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot create discussions in inactive forums",
            )
        
        # Check if user is a member of the forum
        is_member = MembershipRepository.is_member(db, discussion_data.forum_id, user.id)
        if not is_member and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You must be a member of the forum to create discussions",
            )
        
        # Create the discussion
        return DiscussionRepository.create(
            db=db,
            forum_id=discussion_data.forum_id,
            user_id=user.id,
            title=discussion_data.title,
            content=discussion_data.content,
            is_pinned=False,
            is_locked=False,
        )

    @staticmethod
    def get_discussion(db: DbSession, discussion_id: int) -> Discussion:
        """Get a discussion by ID."""
        discussion = DiscussionRepository.get_by_id(db, discussion_id)
        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discussion not found",
            )
        
        # Add comment count later when Comment model is implemented
        # discussion.comment_count = CommentRepository.count_by_discussion_id(db, discussion_id)
        
        return discussion

    @staticmethod
    def update_discussion(
        db: DbSession, discussion_id: int, discussion_data: DiscussionUpdateRequest, user: User
    ) -> Discussion:
        """Update a discussion."""
        # Get the discussion
        discussion = DiscussionService.get_discussion(db, discussion_id)
        
        # Check if discussion is locked
        if discussion.is_locked:
            # Allow admins and moderators to update locked discussions
            is_admin = user.role == UserRole.ADMIN
            is_moderator = MembershipRepository.is_moderator(db, discussion.forum_id, user.id)
            
            if not (is_admin or is_moderator):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Cannot update a locked discussion",
                )
        
        # Check if user is the creator or has special permissions
        if discussion.user_id != user.id:
            is_admin = user.role == UserRole.ADMIN
            is_moderator = MembershipRepository.is_moderator(db, discussion.forum_id, user.id)
            
            if not (is_admin or is_moderator):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the creator, moderators, or admins can update this discussion",
                )
        
        # Update the discussion
        return DiscussionRepository.update(
            db=db,
            discussion=discussion,
            title=discussion_data.title,
            content=discussion_data.content,
        )

    @staticmethod
    def delete_discussion(db: DbSession, discussion_id: int, user: User) -> bool:
        """Delete a discussion."""
        # Get the discussion
        discussion = DiscussionService.get_discussion(db, discussion_id)
        
        # Check if user is the creator or has special permissions
        if discussion.user_id != user.id:
            is_admin = user.role == UserRole.ADMIN
            is_moderator = MembershipRepository.is_moderator(db, discussion.forum_id, user.id)
            
            if not (is_admin or is_moderator):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the creator, moderators, or admins can delete this discussion",
                )
        
        # Delete the discussion
        return DiscussionRepository.delete(db, discussion_id)

    @staticmethod
    def pin_discussion(db: DbSession, discussion_id: int, pin: bool, user: User) -> Discussion:
        """Pin or unpin a discussion."""
        # Get the discussion
        discussion = DiscussionService.get_discussion(db, discussion_id)
        
        # Check if user has special permissions
        is_admin = user.role == UserRole.ADMIN
        is_moderator = MembershipRepository.is_moderator(db, discussion.forum_id, user.id)
        
        if not (is_admin or is_moderator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only moderators or admins can pin or unpin discussions",
            )
        
        # Pin or unpin the discussion
        result = DiscussionRepository.pin_discussion(db, discussion_id, pin)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discussion not found",
            )
        
        return result

    @staticmethod
    def lock_discussion(db: DbSession, discussion_id: int, lock: bool, user: User) -> Discussion:
        """Lock or unlock a discussion."""
        # Get the discussion
        discussion = DiscussionService.get_discussion(db, discussion_id)
        
        # Check if user has special permissions
        is_admin = user.role == UserRole.ADMIN
        is_moderator = MembershipRepository.is_moderator(db, discussion.forum_id, user.id)
        
        if not (is_admin or is_moderator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only moderators or admins can lock or unlock discussions",
            )
        
        # Lock or unlock the discussion
        result = DiscussionRepository.lock_discussion(db, discussion_id, lock)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discussion not found",
            )
        
        return result

    @staticmethod
    def get_forum_discussions(
        db: DbSession,
        forum_id: int,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        is_pinned: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Get all discussions in a forum with pagination, filtering, and sorting."""
        # Check if forum exists
        forum = ForumRepository.get_by_id(db, forum_id)
        if not forum:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forum with ID {forum_id} not found",
            )
        
        discussions = DiscussionRepository.get_by_forum_id(
            db, forum_id, skip=skip, limit=limit, search=search, 
            is_pinned=is_pinned, sort_by=sort_by, sort_desc=sort_desc
        )
        
        total = DiscussionRepository.count_by_forum_id(db, forum_id, search=search, is_pinned=is_pinned)
        
        # Add comment count to each discussion when Comment model is implemented
        
        return {
            "items": discussions,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def get_user_discussions(
        db: DbSession, user_id: int, skip: int = 0, limit: int = 10
    ) -> List[Discussion]:
        """Get all discussions created by a user."""
        return DiscussionRepository.get_by_user_id(db, user_id, skip, limit)
    
    @staticmethod
    def get_discussion(db: DbSession, discussion_id: int, user_id: Optional[int] = None) -> Discussion:
        """Get a discussion by ID with like information."""
        discussion = DiscussionRepository.get_by_id(db, discussion_id)
        if not discussion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Discussion not found",
            )
        
        # Add comment count
        discussion.comment_count = CommentRepository.count_all_by_discussion_id(db, discussion_id)
        
        # Add like count
        discussion.like_count = DiscussionRepository.get_like_count(db, discussion_id)
        
        # Add is_liked_by_user flag if user_id is provided
        if user_id:
            discussion.is_liked_by_user = DiscussionRepository.is_liked_by_user(db, discussion_id, user_id)
        
        return discussion