# File path: app/dto/request/membership_dto.py
from pydantic import BaseModel
from typing import Optional
from app.models.forum_membership import MembershipStatus, MembershipRole

class MembershipUpdateRequest(BaseModel):
    status: Optional[MembershipStatus] = None
    role: Optional[MembershipRole] = None