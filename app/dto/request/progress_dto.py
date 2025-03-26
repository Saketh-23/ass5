# File path: app/dto/request/progress_dto.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, timezone

class ProgressCreateRequest(BaseModel):
    goal_id: int
    date: datetime = Field(default_factory=datetime.now)
    value: float
    notes: Optional[str] = None

    @validator('date')
    def date_not_future(cls, v):
        now = datetime.now()
        
        # Handle timezone mismatch
        if v.tzinfo is not None and now.tzinfo is None:
            now = now.replace(tzinfo=timezone.utc)
        elif v.tzinfo is None and now.tzinfo is not None:
            v = v.replace(tzinfo=timezone.utc)
            
        if v > now:
            raise ValueError('Progress date cannot be in the future')
        return v

class ProgressUpdateRequest(BaseModel):
    date: Optional[datetime] = None
    value: Optional[float] = None
    notes: Optional[str] = None

    @validator('date')
    def date_not_future(cls, v):
        if v is not None:
            now = datetime.now()
            
            # Handle timezone mismatch
            if v.tzinfo is not None and now.tzinfo is None:
                now = now.replace(tzinfo=timezone.utc)
            elif v.tzinfo is None and now.tzinfo is not None:
                v = v.replace(tzinfo=timezone.utc)
                
            if v > now:
                raise ValueError('Progress date cannot be in the future')
        return v