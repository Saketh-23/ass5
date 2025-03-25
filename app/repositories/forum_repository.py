# File path: app/repositories/forum_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from app.models.forum import Forum
from app.models.forum_membership import ForumMembership
from app.models.discussion import Discussion

class ForumRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> Forum:
        """Create a new forum in the database."""
        db_forum = Forum(**kwargs)
        db.add(db_forum)
        db.commit()
        db.refresh(db_forum)
        return db_forum

    @staticmethod
    def get_by_id(db: Session, forum_id: int) -> Optional[Forum]:
        """Get a forum by ID."""
        return db.query(Forum).filter(Forum.id == forum_id).first()

    @staticmethod
    def update(db: Session, forum: Forum, **kwargs) -> Forum:
        """Update a forum's attributes."""
        for key, value in kwargs.items():
            if hasattr(forum, key) and value is not None:
                setattr(forum, key, value)
        
        db.commit()
        db.refresh(forum)
        return forum

    @staticmethod
    def delete(db: Session, forum_id: int) -> bool:
        """Delete a forum by ID."""
        forum = db.query(Forum).filter(Forum.id == forum_id).first()
        if forum:
            db.delete(forum)
            db.commit()
            return True
        return False

    @staticmethod
    def get_all(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> List[Forum]:
        """Get all forums with search and sorting."""
        query = db.query(Forum)
        
        # Apply search
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Forum.name.ilike(search_term) | Forum.description.ilike(search_term)
            )
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Forum, sort_by)))
        else:
            query = query.order_by(asc(getattr(Forum, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count(db: Session, search: Optional[str] = None) -> int:
        """Count forums with applied search."""
        query = db.query(Forum)
        
        # Apply search
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Forum.name.ilike(search_term) | Forum.description.ilike(search_term)
            )
        
        return query.count()

    @staticmethod
    def get_member_count(db: Session, forum_id: int) -> int:
        """Get the number of active members in a forum."""
        return db.query(ForumMembership).filter(
            ForumMembership.forum_id == forum_id,
            ForumMembership.status == "ACTIVE"
        ).count()

    @staticmethod
    def get_discussion_count(db: Session, forum_id: int) -> int:
        """Get the number of discussions in a forum."""
        return db.query(Discussion).filter(Discussion.forum_id == forum_id).count()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Forum]:
        """Get all forums created by a specific user."""
        return db.query(Forum)\
            .filter(Forum.created_by == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()

    @staticmethod
    def get_forums_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Forum]:
        """Get all forums that a user is a member of."""
        # Get forum IDs from user's memberships
        forum_ids_subquery = db.query(ForumMembership.forum_id).filter(
            ForumMembership.user_id == user_id,
            ForumMembership.status == "ACTIVE"
        ).subquery()
        
        return db.query(Forum)\
            .filter(Forum.id.in_(forum_ids_subquery))\
            .offset(skip)\
            .limit(limit)\
            .all()