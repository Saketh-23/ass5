from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_current_admin_user
from app.models.user import User, UserRole
from app.dto.request.user_dto import UserUpdateRequest
from app.dto.response.user_dto import UserResponse
from app.services.user_service import UserService
from app.services.auth_service import AuthService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get the current user's profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_data: UserUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update the current user's profile."""
    updated_user = UserService.update_user(db, current_user, user_data)
    return updated_user


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get a user by ID."""
    # Check if the user is requesting their own profile or is an admin
    if current_user.id != user_id and current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access other user profiles",
        )
    
    user = UserService.get_user_by_id(db, user_id)
    return user


@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all users (admin only)."""
    users = UserService.get_users(db, skip, limit)
    return users


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Delete a user (admin only)."""
    UserService.delete_user(db, user_id)
    return None


@router.put("/{user_id}/role", response_model=UserResponse)
def change_user_role(
    user_id: int,
    role: UserRole,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Change a user's role (admin only)."""
    user = UserService.get_user_by_id(db, user_id)
    updated_user = AuthService.change_user_role(db, user, role)
    return updated_user


@router.get("/search/", response_model=List[UserResponse])
def search_users(
    q: str = Query(..., min_length=1, description="Search term"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Search for users by username, first name, or last name."""
    users = UserService.search_users(db, q, skip, limit)
    return users