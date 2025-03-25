# File path: app/dto/request/program_dto.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from app.models.enums import DifficultyLevel

class ProgramCreateRequest(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    category: str = Field(..., min_length=2, max_length=50)
    difficulty: DifficultyLevel
    duration: int = Field(..., gt=0, description="Duration in weeks")
    image_url: Optional[str] = None

class ProgramUpdateRequest(BaseModel):
    name: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    difficulty: Optional[DifficultyLevel] = None
    duration: Optional[int] = Field(None, gt=0, description="Duration in weeks")
    image_url: Optional[str] = None
    is_active: Optional[bool] = None