# File path: app/repositories/like_repository.py
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.like import Like, LikeTargetType

class LikeRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> Like:
        """Create a new like in the database."""
        db_like = Like(**kwargs)
        db.add(db_like)
        db.commit()
        db.refresh(db_like)
        return db_like

    @staticmethod
    def get_discussion_like(db: Session, discussion_id: int, user_id: int) -> Optional[Like]:
        """Get a like for a discussion by user."""
        return db.query(Like).filter(
            Like.discussion_id == discussion_id,
            Like.user_id == user_id,
            Like.target_type == LikeTargetType.DISCUSSION
        ).first()

    @staticmethod
    def get_comment_like(db: Session, comment_id: int, user_id: int) -> Optional[Like]:
        """Get a like for a comment by user."""
        return db.query(Like).filter(
            Like.comment_id == comment_id,
            Like.user_id == user_id,
            Like.target_type == LikeTargetType.COMMENT
        ).first()

    @staticmethod
    def delete(db: Session, like_id: int) -> bool:
        """Delete a like by ID."""
        like = db.query(Like).filter(Like.id == like_id).first()
        if like:
            db.delete(like)
            db.commit()
            return True
        return False

    @staticmethod
    def count_discussion_likes(db: Session, discussion_id: int) -> int:
        """Count likes for a discussion."""
        return db.query(Like).filter(
            Like.discussion_id == discussion_id,
            Like.target_type == LikeTargetType.DISCUSSION
        ).count()

    @staticmethod
    def count_comment_likes(db: Session, comment_id: int) -> int:
        """Count likes for a comment."""
        return db.query(Like).filter(
            Like.comment_id == comment_id,
            Like.target_type == LikeTargetType.COMMENT
        ).count()

    @staticmethod
    def get_by_user_id(
        db: Session, 
        user_id: int,
        skip: int = 0, 
        limit: int = 100
    ) -> List[Like]:
        """Get all likes by a user."""
        return db.query(Like)\
            .filter(Like.user_id == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()