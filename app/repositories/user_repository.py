from typing import Optional
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.core.security import get_password_hash


class UserRepository:
    @staticmethod
    def create(
        db: Session,
        username: str,
        email: str,
        password: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        role: UserRole = UserRole.USER,
    ) -> User:
        """Create a new user in the database."""
        hashed_password = get_password_hash(password)
        db_user = User(
            username=username,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """Get a user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """Get a user by username."""
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """Get a user by email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def update(db: Session, user: User, **kwargs) -> User:
        """Update a user's attributes."""
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def delete(db: Session, user_id: int) -> bool:
        """Delete a user by ID."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            db.delete(user)
            db.commit()
            return True
        return False

    @staticmethod
    def get_all(db: Session, skip: int = 0, limit: int = 100):
        """Get all users with pagination."""
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def change_password(db: Session, user: User, new_password: str) -> User:
        """Change a user's password."""
        user.password = get_password_hash(new_password)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def change_role(db: Session, user: User, new_role: UserRole) -> User:
        """Change a user's role."""
        user.role = new_role
        db.commit()
        db.refresh(user)
        return user