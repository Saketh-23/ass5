from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.dto.request.user_dto import UserRegisterRequest
from app.repositories.user_repository import UserRepository
from app.core.security import verify_password, create_access_token
from app.core.config import settings


class AuthService:
    @staticmethod
    def register_user(db: Session, user_data: UserRegisterRequest) -> User:
        """Register a new user."""
        # Check if username already exists
        if UserRepository.get_by_username(db, user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered",
            )
        
        # Check if email already exists
        if UserRepository.get_by_email(db, user_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )
        
        # Create the user
        return UserRepository.create(
            db=db,
            username=user_data.username,
            email=user_data.email,
            password=user_data.password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
        )

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate a user and return the user if valid."""
        user = UserRepository.get_by_username(db, username)
        
        if not user:
            return None
        
        if not verify_password(password, user.password):
            return None
        
        return user

    @staticmethod
    def create_user_token(user: User) -> Tuple[str, datetime, Dict[str, Any]]:
        """Create a JWT token for a user."""
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        expires_at = datetime.utcnow() + access_token_expires
        
        # Create the access token
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        # Token data
        token_data = {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds()),
            "user": user,
        }
        
        return access_token, expires_at, token_data

    @staticmethod
    def change_password(db: Session, user: User, current_password: str, new_password: str) -> User:
        """Change a user's password."""
        # Verify current password
        if not verify_password(current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Incorrect password",
            )
        
        # Change the password
        return UserRepository.change_password(db, user, new_password)

    @staticmethod
    def change_user_role(db: Session, user: User, new_role: UserRole) -> User:
        """Change a user's role."""
        return UserRepository.change_role(db, user, new_role)