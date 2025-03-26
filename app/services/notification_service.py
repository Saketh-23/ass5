# app/services/notification_service.py
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.notification import Notification, NotificationType
from app.dto.request.notification_dto import NotificationUpdateRequest
from app.repositories.notification_repository import NotificationRepository

class NotificationService:
    @staticmethod
    def create_notification(
        db: Session,
        user_id: int,
        title: str,
        content: str,
        type: NotificationType,
        goal_id: Optional[int] = None,
        achievement_id: Optional[int] = None
    ) -> Notification:
        """Create a new notification for a user."""
        return NotificationRepository.create(
            db=db,
            user_id=user_id,
            title=title,
            content=content,
            type=type,
            goal_id=goal_id,
            achievement_id=achievement_id,
            is_read=False
        )

    @staticmethod
    def get_notification(db: Session, notification_id: int) -> Notification:
        """Get a notification by ID."""
        notification = NotificationRepository.get_by_id(db, notification_id)
        if not notification:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notification not found",
            )
        
        return notification

    @staticmethod
    def mark_as_read(
        db: Session, notification_id: int, user: User
    ) -> Notification:
        """Mark a notification as read."""
        # Get the notification
        notification = NotificationService.get_notification(db, notification_id)
        
        # Check if notification belongs to user
        if notification.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to update this notification",
            )
        
        # Update the notification
        return NotificationRepository.update(
            db=db,
            notification=notification,
            is_read=True
        )

    @staticmethod
    def mark_all_as_read(db: Session, user_id: int) -> int:
        """Mark all notifications for a user as read and return count of updated records."""
        return NotificationRepository.mark_all_as_read(db, user_id)

    @staticmethod
    def delete_notification(db: Session, notification_id: int, user: User) -> bool:
        """Delete a notification."""
        # Get the notification
        notification = NotificationService.get_notification(db, notification_id)
        
        # Check if notification belongs to user
        if notification.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to delete this notification",
            )
        
        # Delete the notification
        return NotificationRepository.delete(db, notification_id)

    @staticmethod
    def get_user_notifications(
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        is_read: Optional[bool] = None,
        notification_type: Optional[NotificationType] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Get all notifications for a user with pagination, filtering, and sorting."""
        notifications = NotificationRepository.get_by_user_id(
            db, user_id, 
            skip=skip, 
            limit=limit, 
            is_read=is_read,
            notification_type=notification_type,
            sort_by=sort_by, 
            sort_desc=sort_desc
        )
        
        total = NotificationRepository.count_by_user_id(
            db, user_id, 
            is_read=is_read,
            notification_type=notification_type
        )
        
        return {
            "items": notifications,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def get_unread_count(db: Session, user_id: int) -> int:
        """Get count of unread notifications for a user."""
        return NotificationRepository.count_by_user_id(db, user_id, is_read=False)