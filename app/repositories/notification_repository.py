# app/repositories/notification_repository.py

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from datetime import datetime
from app.models.notification import Notification, NotificationType

class NotificationRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> Notification:
        """Create a new notification in the database."""
        db_notification = Notification(**kwargs)
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification

    @staticmethod
    def get_by_id(db: Session, notification_id: int) -> Optional[Notification]:
        """Get a notification by ID."""
        return db.query(Notification).filter(Notification.id == notification_id).first()

    @staticmethod
    def update(db: Session, notification: Notification, **kwargs) -> Notification:
        """Update a notification's attributes."""
        for key, value in kwargs.items():
            if hasattr(notification, key) and value is not None:
                setattr(notification, key, value)
        
        db.commit()
        db.refresh(notification)
        return notification

    @staticmethod
    def delete(db: Session, notification_id: int) -> bool:
        """Delete a notification by ID."""
        notification = db.query(Notification).filter(Notification.id == notification_id).first()
        if notification:
            db.delete(notification)
            db.commit()
            return True
        return False

    @staticmethod
    def get_by_user_id(
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        is_read: Optional[bool] = None,
        notification_type: Optional[NotificationType] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> List[Notification]:
        """Get notifications by user ID with filtering and sorting."""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        # Apply filters
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
            
        if notification_type:
            query = query.filter(Notification.type == notification_type)
            
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Notification, sort_by)))
        else:
            query = query.order_by(asc(getattr(Notification, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_by_user_id(
        db: Session, 
        user_id: int,
        is_read: Optional[bool] = None,
        notification_type: Optional[NotificationType] = None
    ) -> int:
        """Count notifications by user ID with filtering."""
        query = db.query(Notification).filter(Notification.user_id == user_id)
        
        # Apply filters
        if is_read is not None:
            query = query.filter(Notification.is_read == is_read)
            
        if notification_type:
            query = query.filter(Notification.type == notification_type)
            
        return query.count()

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """Mark all notifications for a user as read and return count of updated records."""
        result = db.query(Notification)\
            .filter(Notification.user_id == user_id, Notification.is_read == False)\
            .update({Notification.is_read: True})
            
        db.commit()
        return result