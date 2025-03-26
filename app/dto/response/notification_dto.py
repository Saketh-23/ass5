from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.notification import NotificationType

class NotificationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    content: str
    type: NotificationType
    is_read: bool
    goal_id: Optional[int] = None
    achievement_id: Optional[int] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    page: int
    size: int
    pages: int