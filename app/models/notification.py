# File path: app/models/notification.py

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Enum, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.models.base import Base

class NotificationType(str, enum.Enum):
    GOAL_REMINDER = "GOAL_REMINDER"
    GOAL_COMPLETED = "GOAL_COMPLETED"
    GOAL_DEADLINE = "GOAL_DEADLINE"
    ACHIEVEMENT_UNLOCKED = "ACHIEVEMENT_UNLOCKED"
    PROGRESS_MILESTONE = "PROGRESS_MILESTONE"
    SYSTEM = "SYSTEM"

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    type = Column(Enum(NotificationType), nullable=False)
    is_read = Column(Boolean, default=False, nullable=False)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=True)
    achievement_id = Column(Integer, ForeignKey("achievements.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="notifications")