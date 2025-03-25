# File path: app/dto/response/program_dto.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.enums import DifficultyLevel
from app.dto.response.user_dto import UserResponse

class ProgramResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    category: str
    difficulty: DifficultyLevel
    duration: int
    created_by: int
    is_active: bool
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class ProgramDetailResponse(ProgramResponse):
    creator: Optional[UserResponse] = None

class ProgramListResponse(BaseModel):
    items: List[ProgramResponse]
    total: int
    page: int
    size: int
    pages: int