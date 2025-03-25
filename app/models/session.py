# File path: app/models/session.py
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.base import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    trainer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    total_slots = Column(Integer, nullable=False)
    available_slots = Column(Integer, nullable=False)
    price = Column(Float, nullable=False, default=0.0)
    location = Column(String(255), nullable=True)
    is_virtual = Column(Boolean, default=False, nullable=False)
    meeting_link = Column(String(255), nullable=True)
    is_cancelled = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    program = relationship("Program", back_populates="sessions")
    trainer = relationship("User", back_populates="sessions")
    # bookings = relationship("Booking", back_populates="session", cascade="all, delete-orphan")