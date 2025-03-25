from typing import List, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.dto.request.user_dto import UserUpdateRequest
from app.repositories.user_repository import UserRepository


class UserService:
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        """Get a user by ID."""
        user = UserRepository.get_by_id(db, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return user

    @staticmethod
    def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get all users with pagination."""
        return UserRepository.get_all(db, skip, limit)

    @staticmethod
    def update_user(db: Session, user: User, user_data: UserUpdateRequest) -> User:
        """Update a user's profile."""
        return UserRepository.update(
            db=db,
            user=user,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            bio=user_data.bio,
        )

    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """Delete a user."""
        result = UserRepository.delete(db, user_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        return True

    @staticmethod
    def search_users(
        db: Session, search_term: str, skip: int = 0, limit: int = 100
    ) -> List[User]:
        """Search for users by username, first name, or last name."""
        search_term = f"%{search_term}%"
        return (
            db.query(User)
            .filter(
                (User.username.ilike(search_term))
                | (User.first_name.ilike(search_term))
                | (User.last_name.ilike(search_term))
            )
            .offset(skip)
            .limit(limit)
            .all()
        )