# File path: app/api/v1/endpoints/reviews.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.dto.request.review_dto import ReviewCreateRequest, ReviewUpdateRequest
from app.dto.response.review_dto import (
    ReviewResponse, ReviewDetailResponse, ReviewListResponse,
    ProgramRatingResponse, TrainerRatingResponse
)
from app.services.review_service import ReviewService

router = APIRouter()

@router.post("/programs/{program_id}/reviews", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
def create_review(
    program_id: int,
    review_data: ReviewCreateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Create a new review for a program."""
    # Ensure program_id in path matches the one in request body
    if review_data.program_id != program_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Program ID in path does not match program ID in request body",
        )
    
    review = ReviewService.create_review(db, review_data, current_user)
    return review

@router.get("/programs/{program_id}/reviews", response_model=ReviewListResponse)
def get_program_reviews(
    program_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(rating|created_at)$"),
    sort_desc: bool = True,
    db: DbSession = Depends(get_db),
):
    """Get all reviews for a program."""
    result = ReviewService.get_program_reviews(
        db, program_id, skip=skip, limit=limit, sort_by=sort_by, sort_desc=sort_desc
    )
    return result

@router.get("/programs/{program_id}/rating", response_model=ProgramRatingResponse)
def get_program_rating(
    program_id: int,
    db: DbSession = Depends(get_db),
):
    """Get average rating and count of reviews for a program."""
    average, count = ReviewService.get_program_rating(db, program_id)
    return {
        "program_id": program_id,
        "average_rating": average or 0.0,
        "total_reviews": count or 0
    }

@router.get("/trainers/{trainer_id}/rating", response_model=TrainerRatingResponse)
def get_trainer_rating(
    trainer_id: int,
    db: DbSession = Depends(get_db),
):
    """Get average rating, count of reviews, and count of programs for a trainer."""
    average, count, program_count = ReviewService.get_trainer_rating(db, trainer_id)
    return {
        "trainer_id": trainer_id,
        "average_rating": average or 0.0,
        "total_reviews": count or 0,
        "total_programs": program_count or 0
    }

@router.get("/reviews/{review_id}", response_model=ReviewDetailResponse)
def get_review(
    review_id: int,
    db: DbSession = Depends(get_db),
):
    """Get a specific review."""
    review = ReviewService.get_by_id(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    return review

@router.put("/reviews/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review_data: ReviewUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Update a review."""
    review = ReviewService.update_review(db, review_id, review_data, current_user)
    return review

@router.delete("/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Delete a review."""
    ReviewService.delete_review(db, review_id, current_user)
    return None

@router.get("/users/me/reviews", response_model=ReviewListResponse)
def get_my_reviews(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get all reviews by the current user."""
    result = ReviewService.get_user_reviews(db, current_user.id, skip, limit)
    return result