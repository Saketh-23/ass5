# File path: app/repositories/review_repository.py
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, func
from app.models.review import Review
from app.models.program import Program
from app.models.user import User

class ReviewRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> Review:
        """Create a new review in the database."""
        db_review = Review(**kwargs)
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        return db_review

    @staticmethod
    def get_by_id(db: Session, review_id: int) -> Optional[Review]:
        """Get a review by ID."""
        return db.query(Review).filter(Review.id == review_id).first()

    @staticmethod
    def get_by_user_program(db: Session, user_id: int, program_id: int) -> Optional[Review]:
        """Get a review by user ID and program ID."""
        return db.query(Review).filter(
            Review.user_id == user_id,
            Review.program_id == program_id
        ).first()

    @staticmethod
    def update(db: Session, review: Review, **kwargs) -> Review:
        """Update a review's attributes."""
        for key, value in kwargs.items():
            if hasattr(review, key) and value is not None:
                setattr(review, key, value)
        
        db.commit()
        db.refresh(review)
        return review

    @staticmethod
    def delete(db: Session, review_id: int) -> bool:
        """Delete a review by ID."""
        review = db.query(Review).filter(Review.id == review_id).first()
        if review:
            db.delete(review)
            db.commit()
            return True
        return False

    @staticmethod
    def get_by_program_id(
        db: Session, 
        program_id: int, 
        skip: int = 0, 
        limit: int = 10,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> List[Review]:
        """Get all reviews for a program."""
        query = db.query(Review).filter(Review.program_id == program_id)
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Review, sort_by)))
        else:
            query = query.order_by(asc(getattr(Review, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_by_program_id(db: Session, program_id: int) -> int:
        """Count reviews for a program."""
        return db.query(Review).filter(Review.program_id == program_id).count()

    @staticmethod
    def get_program_rating(db: Session, program_id: int) -> Tuple[Optional[float], int]:
        """Get average rating and count of reviews for a program."""
        result = db.query(
            func.avg(Review.rating).label("average"),
            func.count(Review.id).label("count")
        ).filter(Review.program_id == program_id).first()
        
        return result.average, result.count

    @staticmethod
    def get_trainer_rating(db: Session, trainer_id: int) -> Tuple[Optional[float], int, int]:
        """Get average rating, count of reviews, and count of programs for a trainer."""
        # Get all programs by the trainer
        program_subquery = db.query(Program.id).filter(Program.created_by == trainer_id).subquery()
        
        # Calculate average rating and count from reviews that match those programs
        result = db.query(
            func.avg(Review.rating).label("average"),
            func.count(Review.id).label("count")
        ).filter(Review.program_id.in_(program_subquery)).first()
        
        # Count total programs by the trainer
        program_count = db.query(Program).filter(Program.created_by == trainer_id).count()
        
        return result.average, result.count, program_count

    @staticmethod
    def get_by_user_id(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 10
    ) -> List[Review]:
        """Get all reviews by a user."""
        return db.query(Review)\
            .filter(Review.user_id == user_id)\
            .order_by(desc(Review.created_at))\
            .offset(skip)\
            .limit(limit)\
            .all()

    @staticmethod
    def count_by_user_id(db: Session, user_id: int) -> int:
        """Count reviews by a user."""
        return db.query(Review).filter(Review.user_id == user_id).count()