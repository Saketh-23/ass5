# File path: app/repositories/membership_repository.py
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models.forum_membership import ForumMembership, MembershipStatus, MembershipRole

class MembershipRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> ForumMembership:
        """Create a new forum membership in the database."""
        db_membership = ForumMembership(**kwargs)
        db.add(db_membership)
        db.commit()
        db.refresh(db_membership)
        return db_membership

    @staticmethod
    def get_by_id(db: Session, membership_id: int) -> Optional[ForumMembership]:
        """Get a membership by ID."""
        return db.query(ForumMembership).filter(ForumMembership.id == membership_id).first()

    @staticmethod
    def get_by_forum_and_user(db: Session, forum_id: int, user_id: int) -> Optional[ForumMembership]:
        """Get a membership by forum ID and user ID."""
        return db.query(ForumMembership).filter(
            ForumMembership.forum_id == forum_id,
            ForumMembership.user_id == user_id
        ).first()

    @staticmethod
    def update(db: Session, membership: ForumMembership, **kwargs) -> ForumMembership:
        """Update a membership's attributes."""
        for key, value in kwargs.items():
            if hasattr(membership, key) and value is not None:
                setattr(membership, key, value)
        
        db.commit()
        db.refresh(membership)
        return membership

    @staticmethod
    def delete(db: Session, membership_id: int) -> bool:
        """Delete a membership by ID."""
        membership = db.query(ForumMembership).filter(ForumMembership.id == membership_id).first()
        if membership:
            db.delete(membership)
            db.commit()
            return True
        return False

    @staticmethod
    def get_by_forum_id(
        db: Session, 
        forum_id: int, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[MembershipStatus] = None,
        role: Optional[MembershipRole] = None
    ) -> List[ForumMembership]:
        """Get all memberships for a forum."""
        query = db.query(ForumMembership).filter(ForumMembership.forum_id == forum_id)
        
        if status:
            query = query.filter(ForumMembership.status == status)
            
        if role:
            query = query.filter(ForumMembership.role == role)
            
        return query.order_by(asc(ForumMembership.join_date)).offset(skip).limit(limit).all()

    @staticmethod
    def count_by_forum_id(
        db: Session,
        forum_id: int,
        status: Optional[MembershipStatus] = None,
        role: Optional[MembershipRole] = None
    ) -> int:
        """Count memberships for a forum."""
        query = db.query(ForumMembership).filter(ForumMembership.forum_id == forum_id)
        
        if status:
            query = query.filter(ForumMembership.status == status)
            
        if role:
            query = query.filter(ForumMembership.role == role)
            
        return query.count()

    @staticmethod
    def get_by_user_id(
        db: Session, 
        user_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[ForumMembership]:
        """Get all memberships for a user."""
        return db.query(ForumMembership)\
            .filter(ForumMembership.user_id == user_id)\
            .order_by(asc(ForumMembership.join_date))\
            .offset(skip)\
            .limit(limit)\
            .all()

    @staticmethod
    def is_moderator(db: Session, forum_id: int, user_id: int) -> bool:
        """Check if a user is a moderator of a forum."""
        membership = db.query(ForumMembership).filter(
            ForumMembership.forum_id == forum_id,
            ForumMembership.user_id == user_id,
            ForumMembership.status == MembershipStatus.ACTIVE,
            ForumMembership.role == MembershipRole.MODERATOR
        ).first()
        
        return membership is not None

    @staticmethod
    def is_member(db: Session, forum_id: int, user_id: int) -> bool:
        """Check if a user is a member of a forum."""
        membership = db.query(ForumMembership).filter(
            ForumMembership.forum_id == forum_id,
            ForumMembership.user_id == user_id,
            ForumMembership.status == MembershipStatus.ACTIVE
        ).first()
        
        return membership is not None