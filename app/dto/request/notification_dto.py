# File path: app/dto/request/notification_dto.py
from pydantic import BaseModel, Field
from typing import Optional
from app.models.notification import NotificationType

class NotificationCreateRequest(BaseModel):
    user_id: int
    title: str = Field(..., min_length=3, max_length=100)
    content: str = Field(..., min_length=1)
    type: NotificationType
    goal_id: Optional[int] = None
    achievement_id: Optional[int] = None

class NotificationUpdateRequest(BaseModel):
    is_read: bool = True