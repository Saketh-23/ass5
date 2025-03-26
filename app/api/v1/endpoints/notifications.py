# app/api/v1/endpoints/notifications.py

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.notification import NotificationType
from app.dto.request.notification_dto import NotificationUpdateRequest
from app.dto.response.notification_dto import NotificationResponse, NotificationListResponse
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("", response_model=NotificationListResponse)
def get_my_notifications(
    is_read: Optional[bool] = None,
    type: Optional[NotificationType] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(created_at)$"),
    sort_desc: bool = True,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get notifications for the current user."""
    result = NotificationService.get_user_notifications(
        db, current_user.id, 
        skip=skip, 
        limit=limit, 
        is_read=is_read,
        notification_type=type,
        sort_by=sort_by, 
        sort_desc=sort_desc
    )
    
    return result

@router.get("/count", response_model=int)
def get_unread_count(
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get count of unread notifications for the current user."""
    count = NotificationService.get_unread_count(db, current_user.id)
    return count

@router.put("/mark-all-read", response_model=int)
def mark_all_as_read(
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Mark all notifications as read and return the count of updated notifications."""
    count = NotificationService.mark_all_as_read(db, current_user.id)
    return count

@router.put("/{notification_id}/read", response_model=NotificationResponse)
def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Mark a notification as read."""
    notification = NotificationService.mark_as_read(db, notification_id, current_user)
    return notification

@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Delete a notification."""
    NotificationService.delete_notification(db, notification_id, current_user)
    return None