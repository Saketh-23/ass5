# File path: app/models/forum_membership.py
from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.models.base import Base

class MembershipStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"

class MembershipRole(str, enum.Enum):
    MEMBER = "MEMBER"
    MODERATOR = "MODERATOR"

class ForumMembership(Base):
    __tablename__ = "forum_memberships"

    id = Column(Integer, primary_key=True, index=True)
    forum_id = Column(Integer, ForeignKey("forums.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    join_date = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(MembershipStatus), default=MembershipStatus.ACTIVE, nullable=False)
    role = Column(Enum(MembershipRole), default=MembershipRole.MEMBER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    forum = relationship("Forum", back_populates="memberships")
    user = relationship("User", back_populates="forum_memberships")