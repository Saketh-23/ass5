# File path: app/core/init_db.py
from sqlalchemy.orm import Session
from app.models.enums import UserRole
from app.repositories.user_repository import UserRepository
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

def create_first_admin(db: Session) -> None:
    """Create an admin user if it doesn't exist."""
    admin = UserRepository.get_by_username(db, "admin")
    if not admin:
        logger.info("Creating admin user")
        UserRepository.create(
            db=db,
            username="admin",
            email="admin@connectfit.com",
            password="Admin123",  # This should be changed after first login
            first_name="Admin",
            last_name="User",
            role=UserRole.ADMIN
        )
        logger.info("Admin user created")
    else:
        logger.info("Admin user already exists")

def create_demo_trainer(db: Session) -> None:
    """Create a demo trainer if it doesn't exist."""
    trainer = UserRepository.get_by_username(db, "trainer")
    if not trainer:
        logger.info("Creating trainer user")
        UserRepository.create(
            db=db,
            username="trainer",
            email="trainer@connectfit.com",
            password="Trainer123",  # This should be changed after first login
            first_name="Demo",
            last_name="Trainer",
            role=UserRole.TRAINER
        )
        logger.info("Trainer user created")
    else:
        logger.info("Trainer user already exists")

def create_demo_user(db: Session) -> None:
    """Create a demo regular user if it doesn't exist."""
    user = UserRepository.get_by_username(db, "user")
    if not user:
        logger.info("Creating demo user")
        UserRepository.create(
            db=db,
            username="user",
            email="user@connectfit.com",
            password="User123",  # This should be changed after first login
            first_name="Demo",
            last_name="User",
            role=UserRole.USER
        )
        logger.info("Demo user created")
    else:
        logger.info("Demo user already exists")

def init_db(db: Session) -> None:
    """Initialize database with default users."""
    create_first_admin(db)
    create_demo_trainer(db)
    create_demo_user(db)