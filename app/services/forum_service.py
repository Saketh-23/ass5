# File path: app/services/forum_service.py
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.models.forum import Forum
from app.models.user import User, UserRole
from app.dto.request.forum_dto import ForumCreateRequest, ForumUpdateRequest
from app.repositories.forum_repository import ForumRepository
from app.repositories.membership_repository import MembershipRepository

class ForumService:
    @staticmethod
    def create_forum(db: DbSession, forum_data: ForumCreateRequest, user: User) -> Forum:
        """Create a new forum."""
        # Check if user is a trainer or admin
        if user.role not in [UserRole.TRAINER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only trainers and admins can create forums",
            )
        
        # Create the forum
        forum = ForumRepository.create(
            db=db,
            name=forum_data.name,
            description=forum_data.description,
            created_by=user.id,
        )
        
        # Add the creator as a moderator
        MembershipRepository.create(
            db=db,
            forum_id=forum.id,
            user_id=user.id,
            role="MODERATOR"
        )
        
        return forum

    @staticmethod
    def get_forum(db: DbSession, forum_id: int) -> Forum:
        """Get a forum by ID with membership and discussion counts."""
        forum = ForumRepository.get_by_id(db, forum_id)
        if not forum:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Forum not found",
            )
        
        # Add member and discussion counts
        forum.member_count = ForumRepository.get_member_count(db, forum_id)
        forum.discussion_count = ForumRepository.get_discussion_count(db, forum_id)
        
        return forum

    @staticmethod
    def update_forum(
        db: DbSession, forum_id: int, forum_data: ForumUpdateRequest, user: User
    ) -> Forum:
        """Update a forum."""
        # Get the forum
        forum = ForumService.get_forum(db, forum_id)
        
        # Check if user is the creator or an admin
        if forum.created_by != user.id and user.role != UserRole.ADMIN:
            # Check if user is a moderator
            is_moderator = MembershipRepository.is_moderator(db, forum_id, user.id)
            if not is_moderator:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the creator, a moderator, or an admin can update this forum",
                )
        
        # Update the forum
        return ForumRepository.update(
            db=db,
            forum=forum,
            name=forum_data.name,
            description=forum_data.description,
            is_active=forum_data.is_active,
        )

    @staticmethod
    def delete_forum(db: DbSession, forum_id: int, user: User) -> bool:
        """Delete a forum."""
        # Get the forum
        forum = ForumService.get_forum(db, forum_id)
        
        # Check if user is the creator or an admin
        if forum.created_by != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the creator or an admin can delete this forum",
            )
        
        # Delete the forum
        return ForumRepository.delete(db, forum_id)

    @staticmethod
    def get_forums(
        db: DbSession,
        skip: int = 0,
        limit: int = 10,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Get all forums with search, sorting, and pagination."""
        forums = ForumRepository.get_all(
            db, skip=skip, limit=limit, search=search, sort_by=sort_by, sort_desc=sort_desc
        )
        
        total = ForumRepository.count(db, search=search)
        
        # Add member and discussion counts to each forum
        for forum in forums:
            forum.member_count = ForumRepository.get_member_count(db, forum.id)
            forum.discussion_count = ForumRepository.get_discussion_count(db, forum.id)
        
        return {
            "items": forums,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def get_user_forums(
        db: DbSession, user_id: int, skip: int = 0, limit: int = 10
    ) -> List[Forum]:
        """Get all forums created by a specific user."""
        return ForumRepository.get_by_user_id(db, user_id, skip, limit)
        
    @staticmethod
    def get_user_memberships(
        db: DbSession, user_id: int, skip: int = 0, limit: int = 10
    ) -> List[Forum]:
        """Get all forums that a user is a member of."""
        return ForumRepository.get_forums_for_user(db, user_id, skip, limit)