# app/models/goal.py
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Text, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.models.base import Base

class GoalStatus(str, enum.Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    MISSED = "MISSED"

class GoalType(str, enum.Enum):
    WEIGHT_LOSS = "WEIGHT_LOSS"
    MUSCLE_GAIN = "MUSCLE_GAIN"
    CARDIO = "CARDIO"
    STRENGTH = "STRENGTH"
    FLEXIBILITY = "FLEXIBILITY"
    ENDURANCE = "ENDURANCE"
    CUSTOM = "CUSTOM"

class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    goal_type = Column(Enum(GoalType), default=GoalType.CUSTOM, nullable=False)
    target_value = Column(Float, nullable=True)
    start_date = Column(DateTime(timezone=True), nullable=False)
    deadline = Column(DateTime(timezone=True), nullable=True)
    status = Column(Enum(GoalStatus), default=GoalStatus.IN_PROGRESS, nullable=False)
    is_public = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="goals")
    progress_entries = relationship("Progress", back_populates="goal", cascade="all, delete-orphan")
    achievements = relationship("Achievement", back_populates="goal")