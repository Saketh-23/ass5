# File path: app/repositories/discussion_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models.discussion import Discussion
from app.models.like import Like, LikeTargetType

class DiscussionRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> Discussion:
        """Create a new discussion in the database."""
        db_discussion = Discussion(**kwargs)
        db.add(db_discussion)
        db.commit()
        db.refresh(db_discussion)
        return db_discussion

    @staticmethod
    def get_by_id(db: Session, discussion_id: int) -> Optional[Discussion]:
        """Get a discussion by ID."""
        return db.query(Discussion).filter(Discussion.id == discussion_id).first()

    @staticmethod
    def update(db: Session, discussion: Discussion, **kwargs) -> Discussion:
        """Update a discussion's attributes."""
        for key, value in kwargs.items():
            if hasattr(discussion, key) and value is not None:
                setattr(discussion, key, value)
        
        db.commit()
        db.refresh(discussion)
        return discussion

    @staticmethod
    def delete(db: Session, discussion_id: int) -> bool:
        """Delete a discussion by ID."""
        discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
        if discussion:
            db.delete(discussion)
            db.commit()
            return True
        return False

    @staticmethod
    def get_by_forum_id(
        db: Session, 
        forum_id: int, 
        skip: int = 0, 
        limit: int = 100,
        search: Optional[str] = None,
        is_pinned: Optional[bool] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> List[Discussion]:
        """Get all discussions for a forum."""
        query = db.query(Discussion).filter(Discussion.forum_id == forum_id)
        
        # Apply search
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Discussion.title.ilike(search_term) | Discussion.content.ilike(search_term)
            )
            
        # Filter by pinned status
        if is_pinned is not None:
            query = query.filter(Discussion.is_pinned == is_pinned)
            
        # If sorting by created_at and we want pinned discussions at top
        if sort_by == "created_at" and is_pinned is None:
            query = query.order_by(desc(Discussion.is_pinned))
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Discussion, sort_by)))
        else:
            query = query.order_by(asc(getattr(Discussion, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_by_forum_id(
        db: Session,
        forum_id: int,
        search: Optional[str] = None,
        is_pinned: Optional[bool] = None
    ) -> int:
        """Count discussions for a forum."""
        query = db.query(Discussion).filter(Discussion.forum_id == forum_id)
        
        # Apply search
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                Discussion.title.ilike(search_term) | Discussion.content.ilike(search_term)
            )
            
        # Filter by pinned status
        if is_pinned is not None:
            query = query.filter(Discussion.is_pinned == is_pinned)
            
        return query.count()

    @staticmethod
    def get_by_user_id(
        db: Session, 
        user_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Discussion]:
        """Get all discussions created by a user."""
        return db.query(Discussion)\
            .filter(Discussion.user_id == user_id)\
            .order_by(desc(Discussion.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

    @staticmethod
    def pin_discussion(db: Session, discussion_id: int, pin: bool = True) -> Optional[Discussion]:
        """Pin or unpin a discussion."""
        discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
        if discussion:
            discussion.is_pinned = pin
            db.commit()
            db.refresh(discussion)
            return discussion
        return None

    @staticmethod
    def lock_discussion(db: Session, discussion_id: int, lock: bool = True) -> Optional[Discussion]:
        """Lock or unlock a discussion."""
        discussion = db.query(Discussion).filter(Discussion.id == discussion_id).first()
        if discussion:
            discussion.is_locked = lock
            db.commit()
            db.refresh(discussion)
            return discussion
        return None
    
    @staticmethod
    def get_like_count(db: Session, discussion_id: int) -> int:
        """Get the number of likes for a discussion."""
        return db.query(Like).filter(
            Like.discussion_id == discussion_id,
            Like.target_type == LikeTargetType.DISCUSSION
        ).count()

    @staticmethod
    def is_liked_by_user(db: Session, discussion_id: int, user_id: int) -> bool:
        """Check if a discussion is liked by a specific user."""
        like = db.query(Like).filter(
            Like.discussion_id == discussion_id,
            Like.user_id == user_id,
            Like.target_type == LikeTargetType.DISCUSSION
        ).first()
        
        return like is not None