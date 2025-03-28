# File path: app/models/user.py
from sqlalchemy import Column, String, Integer, DateTime, Enum, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.models.base import Base
from app.models.enums import UserRole

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)  # Will store hashed password
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    bio = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Add relationship to Program
    programs = relationship("Program", back_populates="creator")
    sessions = relationship("Session", back_populates="trainer")
    bookings = relationship("Booking", back_populates="user")
    # payments = relationship("Payment", back_populates="user")
    reviews = relationship("Review", back_populates="user")
    forums = relationship("Forum", back_populates="creator")
    forum_memberships = relationship("ForumMembership", back_populates="user")
    discussions = relationship("Discussion", back_populates="user")
    comments = relationship("Comment", back_populates="user")
    likes = relationship("Like", back_populates="user")
    goals = relationship("Goal", back_populates="user")
    achievements = relationship("Achievement", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
    chat_messages = relationship("ChatMessage", back_populates="user")
    meal_logs = relationship("MealLog", back_populates="user")
