# File path: app/services/membership_service.py
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.models.forum_membership import ForumMembership, MembershipStatus, MembershipRole
from app.models.user import User, UserRole
from app.dto.request.membership_dto import MembershipUpdateRequest
from app.repositories.forum_repository import ForumRepository
from app.repositories.membership_repository import MembershipRepository

class MembershipService:
    @staticmethod
    def join_forum(db: DbSession, forum_id: int, user: User) -> ForumMembership:
        """Join a forum."""
        # Check if forum exists
        forum = ForumRepository.get_by_id(db, forum_id)
        if not forum:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forum with ID {forum_id} not found",
            )
        
        # Check if user is already a member
        existing_membership = MembershipRepository.get_by_forum_and_user(db, forum_id, user.id)
        if existing_membership:
            if existing_membership.status == MembershipStatus.ACTIVE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You are already a member of this forum",
                )
            
            # If previously blocked, allow rejoining only if admin or trainer
            if existing_membership.status == MembershipStatus.BLOCKED and user.role not in [UserRole.ADMIN, UserRole.TRAINER]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Your membership to this forum has been blocked",
                )
            
            # Reactivate membership
            return MembershipRepository.update(
                db=db,
                membership=existing_membership,
                status=MembershipStatus.ACTIVE,
            )
        
        # Create new membership
        return MembershipRepository.create(
            db=db,
            forum_id=forum_id,
            user_id=user.id,
            status=MembershipStatus.ACTIVE,
            role=MembershipRole.MEMBER,
        )

    @staticmethod
    def leave_forum(db: DbSession, forum_id: int, user: User) -> bool:
        """Leave a forum."""
        # Check if forum exists
        forum = ForumRepository.get_by_id(db, forum_id)
        if not forum:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forum with ID {forum_id} not found",
            )
        
        # Check if user is a member
        membership = MembershipRepository.get_by_forum_and_user(db, forum_id, user.id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are not a member of this forum",
            )
        
        # Check if user is the forum creator
        if forum.created_by == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Forum creators cannot leave their own forums",
            )
        
        # Delete membership
        return MembershipRepository.delete(db, membership.id)

    @staticmethod
    def update_membership(
        db: DbSession, forum_id: int, member_id: int, membership_data: MembershipUpdateRequest, user: User
    ) -> ForumMembership:
        """Update a membership."""
        # Check if forum exists
        forum = ForumRepository.get_by_id(db, forum_id)
        if not forum:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forum with ID {forum_id} not found",
            )
        
        # Check if membership exists
        membership = MembershipRepository.get_by_forum_and_user(db, forum_id, member_id)
        if not membership:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {member_id} is not a member of this forum",
            )
        
        # Check permissions
        is_admin = user.role == UserRole.ADMIN
        is_creator = forum.created_by == user.id
        is_moderator = MembershipRepository.is_moderator(db, forum_id, user.id)
        
        if not (is_admin or is_creator or is_moderator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the forum creator, moderators, or admins can update memberships",
            )
        
        # Forum creators can't be blocked or demoted
        if forum.created_by == member_id:
            if (membership_data.status == MembershipStatus.BLOCKED or 
                (membership_data.role == MembershipRole.MEMBER and membership.role == MembershipRole.MODERATOR)):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Forum creators cannot be blocked or demoted",
                )
        
        # Only creators and admins can promote to moderator
        if (membership_data.role == MembershipRole.MODERATOR and 
            membership.role == MembershipRole.MEMBER and 
            not (is_admin or is_creator)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the forum creator or admins can promote members to moderators",
            )
        
        # Update the membership
        return MembershipRepository.update(
            db=db,
            membership=membership,
            status=membership_data.status,
            role=membership_data.role,
        )

    @staticmethod
    def get_forum_members(
        db: DbSession,
        forum_id: int,
        skip: int = 0,
        limit: int = 10,
        status: Optional[MembershipStatus] = MembershipStatus.ACTIVE,
        role: Optional[MembershipRole] = None,
    ) -> Dict[str, Any]:
        """Get all members of a forum with pagination and filtering."""
        # Check if forum exists
        forum = ForumRepository.get_by_id(db, forum_id)
        if not forum:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Forum with ID {forum_id} not found",
            )
        
        memberships = MembershipRepository.get_by_forum_id(
            db, forum_id, skip=skip, limit=limit, status=status, role=role
        )
        
        total = MembershipRepository.count_by_forum_id(db, forum_id, status=status, role=role)
        
        return {
            "items": memberships,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def get_user_memberships(
        db: DbSession, user_id: int, skip: int = 0, limit: int = 10
    ) -> List[ForumMembership]:
        """Get all forum memberships for a user."""
        return MembershipRepository.get_by_user_id(db, user_id, skip, limit)