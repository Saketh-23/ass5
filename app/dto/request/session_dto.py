# File path: app/dto/request/session_dto.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

class SessionCreateRequest(BaseModel):
    program_id: int
    title: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    total_slots: int = Field(..., gt=0)
    price: float = Field(..., ge=0)
    location: Optional[str] = None
    is_virtual: bool = False
    meeting_link: Optional[str] = None
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v
    
    @validator('meeting_link')
    def validate_meeting_link(cls, v, values):
        if values.get('is_virtual', False) and not v:
            raise ValueError('Meeting link is required for virtual sessions')
        return v

class SessionUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=100)
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    total_slots: Optional[int] = Field(None, gt=0)
    price: Optional[float] = Field(None, ge=0)
    location: Optional[str] = None
    is_virtual: Optional[bool] = None
    meeting_link: Optional[str] = None
    
    @validator('end_time')
    def end_time_must_be_after_start_time(cls, v, values):
        if 'start_time' in values and values['start_time'] is not None and v <= values['start_time']:
            raise ValueError('End time must be after start time')
        return v