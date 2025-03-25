# File path: app/services/review_service.py
from typing import List, Optional, Dict, Any, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DbSession

from app.models.review import Review
from app.models.user import User
from app.dto.request.review_dto import ReviewCreateRequest, ReviewUpdateRequest
from app.repositories.review_repository import ReviewRepository
from app.repositories.program_repository import ProgramRepository
from app.repositories.booking_repository import BookingRepository

class ReviewService:
    @staticmethod
    def create_review(db: DbSession, review_data: ReviewCreateRequest, user: User) -> Review:
        """Create a new review for a program."""
        # Check if program exists
        program = ProgramRepository.get_by_id(db, review_data.program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {review_data.program_id} not found",
            )
        
        # Check if user has booked this program's sessions
        # This is a simple check - you might want to make it more sophisticated
        # like checking if they've attended or completed a session
        user_bookings = BookingRepository.get_by_user_id(db, user.id)
        program_session_ids = [session.id for session in program.sessions]
        
        has_booked = any(booking.session_id in program_session_ids for booking in user_bookings)
        
        if not has_booked and user.role not in ["ADMIN", "TRAINER"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only review programs you have participated in",
            )
        
        # Check if user has already reviewed this program
        existing_review = ReviewRepository.get_by_user_program(db, user.id, review_data.program_id)
        if existing_review:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already reviewed this program",
            )
        
        # Create the review
        return ReviewRepository.create(
            db=db,
            user_id=user.id,
            program_id=review_data.program_id,
            rating=review_data.rating,
            comment=review_data.comment,
        )

    @staticmethod
    def update_review(
        db: DbSession, review_id: int, review_data: ReviewUpdateRequest, user: User
    ) -> Review:
        """Update a review."""
        # Get the review
        review = ReviewRepository.get_by_id(db, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        
        # Check if user is the owner or an admin
        if review.user_id != user.id and user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only update your own reviews",
            )
        
        # Update the review
        return ReviewRepository.update(
            db=db,
            review=review,
            rating=review_data.rating,
            comment=review_data.comment,
        )

    @staticmethod
    def delete_review(db: DbSession, review_id: int, user: User) -> bool:
        """Delete a review."""
        # Get the review
        review = ReviewRepository.get_by_id(db, review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Review not found",
            )
        
        # Check if user is the owner or an admin
        if review.user_id != user.id and user.role != "ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only delete your own reviews",
            )
        
        # Delete the review
        return ReviewRepository.delete(db, review_id)

    @staticmethod
    def get_program_reviews(
        db: DbSession,
        program_id: int,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Get all reviews for a program with pagination and sorting."""
        # Check if program exists
        program = ProgramRepository.get_by_id(db, program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found",
            )
        
        reviews = ReviewRepository.get_by_program_id(
            db, program_id, skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
        )
        
        total = ReviewRepository.count_by_program_id(db, program_id)
        
        return {
            "items": reviews,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def get_program_rating(db: DbSession, program_id: int) -> Tuple[Optional[float], int]:
        """Get average rating and count of reviews for a program."""
        # Check if program exists
        program = ProgramRepository.get_by_id(db, program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found",
            )
        
        return ReviewRepository.get_program_rating(db, program_id)

    @staticmethod
    def get_trainer_rating(db: DbSession, trainer_id: int) -> Tuple[Optional[float], int, int]:
        """Get average rating, count of reviews, and count of programs for a trainer."""
        # Check if trainer exists
        user = db.query(User).filter(User.id == trainer_id).first()
        if not user or user.role != "TRAINER":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Trainer with ID {trainer_id} not found",
            )
        
        return ReviewRepository.get_trainer_rating(db, trainer_id)

    @staticmethod
    def get_user_reviews(
        db: DbSession, user_id: int, skip: int = 0, limit: int = 10
    ) -> Dict[str, Any]:
        """Get all reviews by a user with pagination."""
        reviews = ReviewRepository.get_by_user_id(db, user_id, skip, limit)
        
        total = ReviewRepository.count_by_user_id(db, user_id)
        
        return {
            "items": reviews,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }