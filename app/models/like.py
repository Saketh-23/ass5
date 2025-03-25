# File path: app/models/like.py
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.models.base import Base

class LikeTargetType(str, enum.Enum):
    DISCUSSION = "DISCUSSION"
    COMMENT = "COMMENT"

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_type = Column(Enum(LikeTargetType), nullable=False)
    discussion_id = Column(Integer, ForeignKey("discussions.id"), nullable=True)
    comment_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="likes")
    discussion = relationship("Discussion", back_populates="likes")
    comment = relationship("Comment", back_populates="likes")