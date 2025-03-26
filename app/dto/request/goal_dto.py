# File path: app/dto/request/goal_dto.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime, timezone, timedelta
from app.models.goal import GoalType, GoalStatus

class GoalCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = None
    goal_type: GoalType = GoalType.CUSTOM
    target_value: Optional[float] = None
    start_date: datetime = Field(default_factory=datetime.now)
    deadline: Optional[datetime] = None
    is_public: bool = False

    @validator('deadline')
    def deadline_must_be_future(cls, v, values):
        if v is not None:
            # Ensure both datetimes are timezone-aware or timezone-naive for comparison
            now = datetime.now()
            
            # Handle timezone mismatch
            if v.tzinfo is not None and now.tzinfo is None:
                now = now.replace(tzinfo=timezone.utc)
            elif v.tzinfo is None and now.tzinfo is not None:
                v = v.replace(tzinfo=timezone.utc)
                
            start_date = values.get('start_date')
            if start_date:
                # Handle timezone mismatch for start_date
                if v.tzinfo is not None and start_date.tzinfo is None:
                    start_date = start_date.replace(tzinfo=timezone.utc)
                elif v.tzinfo is None and start_date.tzinfo is not None:
                    v = v.replace(tzinfo=timezone.utc)
                    
                if v <= start_date:
                    raise ValueError('Deadline must be after start date')
            
            if v <= now:
                raise ValueError('Deadline must be in the future')
        return v

    @validator('target_value')
    def validate_target_value(cls, v, values):
        goal_type = values.get('goal_type')
        if goal_type != GoalType.CUSTOM and v is None:
            raise ValueError(f'Target value is required for {goal_type} goal type')
        return v

class GoalUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = None
    goal_type: Optional[GoalType] = None
    target_value: Optional[float] = None
    deadline: Optional[datetime] = None
    status: Optional[GoalStatus] = None
    is_public: Optional[bool] = None

    @validator('deadline')
    def deadline_must_be_future(cls, v, values):
        if v is not None:
            # Ensure both datetimes are timezone-aware or timezone-naive for comparison
            now = datetime.now()
            
            # Handle timezone mismatch
            if v.tzinfo is not None and now.tzinfo is None:
                now = now.replace(tzinfo=timezone.utc)
            elif v.tzinfo is None and now.tzinfo is not None:
                v = v.replace(tzinfo=timezone.utc)
                
            if v <= now:
                raise ValueError('Deadline must be in the future')
        return v