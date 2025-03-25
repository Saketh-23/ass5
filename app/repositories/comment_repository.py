# File path: app/repositories/comment_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from app.models.comment import Comment
from app.models.like import Like, LikeTargetType

class CommentRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> Comment:
        """Create a new comment in the database."""
        db_comment = Comment(**kwargs)
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
        return db_comment

    @staticmethod
    def get_by_id(db: Session, comment_id: int) -> Optional[Comment]:
        """Get a comment by ID."""
        return db.query(Comment).filter(Comment.id == comment_id).first()

    @staticmethod
    def update(db: Session, comment: Comment, **kwargs) -> Comment:
        """Update a comment's attributes."""
        for key, value in kwargs.items():
            if hasattr(comment, key) and value is not None:
                setattr(comment, key, value)
        
        db.commit()
        db.refresh(comment)
        return comment

    @staticmethod
    def delete(db: Session, comment_id: int) -> bool:
        """Delete a comment by ID."""
        comment = db.query(Comment).filter(Comment.id == comment_id).first()
        if comment:
            db.delete(comment)
            db.commit()
            return True
        return False

    @staticmethod
    def get_by_discussion_id(
        db: Session, 
        discussion_id: int, 
        parent_id: Optional[int] = None,
        skip: int = 0, 
        limit: int = 100,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> List[Comment]:
        """Get comments for a discussion, optionally filtered by parent_id."""
        query = db.query(Comment).filter(Comment.discussion_id == discussion_id)
        
        # Filter by parent_id (None for top-level comments)
        query = query.filter(Comment.parent_id == parent_id)
            
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Comment, sort_by)))
        else:
            query = query.order_by(asc(getattr(Comment, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_by_discussion_id(
        db: Session, 
        discussion_id: int,
        parent_id: Optional[int] = None
    ) -> int:
        """Count comments for a discussion, optionally filtered by parent_id."""
        query = db.query(Comment).filter(Comment.discussion_id == discussion_id)
        
        # Filter by parent_id (None for top-level comments)
        query = query.filter(Comment.parent_id == parent_id)
            
        return query.count()

    @staticmethod
    def count_all_by_discussion_id(db: Session, discussion_id: int) -> int:
        """Count all comments for a discussion (including replies)."""
        return db.query(Comment).filter(Comment.discussion_id == discussion_id).count()

    @staticmethod
    def get_replies(
        db: Session, 
        comment_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Comment]:
        """Get replies to a comment."""
        return db.query(Comment)\
            .filter(Comment.parent_id == comment_id)\
            .order_by(asc(Comment.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

    @staticmethod
    def count_replies(db: Session, comment_id: int) -> int:
        """Count replies to a comment."""
        return db.query(Comment).filter(Comment.parent_id == comment_id).count()

    @staticmethod
    def get_like_count(db: Session, comment_id: int) -> int:
        """Get the number of likes for a comment."""
        return db.query(Like).filter(
            Like.comment_id == comment_id,
            Like.target_type == LikeTargetType.COMMENT
        ).count()

    @staticmethod
    def is_liked_by_user(db: Session, comment_id: int, user_id: int) -> bool:
        """Check if a comment is liked by a specific user."""
        like = db.query(Like).filter(
            Like.comment_id == comment_id,
            Like.user_id == user_id,
            Like.target_type == LikeTargetType.COMMENT
        ).first()
        
        return like is not None

    @staticmethod
    def get_by_user_id(
        db: Session, 
        user_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Comment]:
        """Get all comments by a user."""
        return db.query(Comment)\
            .filter(Comment.user_id == user_id)\
            .order_by(desc(Comment.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()