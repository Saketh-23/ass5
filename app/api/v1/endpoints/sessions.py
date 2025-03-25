# File path: app/api/v1/endpoints/sessions.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user, get_current_trainer_user
from app.models.user import User
from app.dto.request.session_dto import SessionCreateRequest, SessionUpdateRequest
from app.dto.response.session_dto import SessionResponse, SessionDetailResponse, SessionListResponse
from app.services.session_service import SessionService

router = APIRouter()

@router.post("/programs/{program_id}/sessions", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    program_id: int,
    session_data: SessionCreateRequest,
    current_user: User = Depends(get_current_trainer_user),
    db: DbSession = Depends(get_db),
):
    """Create a new session for a program (trainer only)."""
    # Ensure program_id in path matches the one in the request
    if session_data.program_id != program_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Program ID in path does not match program ID in request body",
        )
    
    session = SessionService.create_session(db, session_data, current_user)
    return session

@router.get("/programs/{program_id}/sessions", response_model=SessionListResponse)
def get_program_sessions(
    program_id: int,
    is_cancelled: Optional[bool] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    has_available_slots: Optional[bool] = None,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("start_time", regex="^(title|start_time|end_time|price|available_slots)$"),
    sort_desc: bool = False,
    db: DbSession = Depends(get_db),
):
    """Get all sessions for a program with filtering and sorting."""
    filters = {}
    
    if is_cancelled is not None:
        filters["is_cancelled"] = is_cancelled
        
    if start_date:
        filters["start_date"] = datetime.combine(start_date, datetime.min.time())
        
    if end_date:
        filters["end_date"] = datetime.combine(end_date, datetime.max.time())
        
    if has_available_slots is not None:
        filters["has_available_slots"] = has_available_slots
        
    if search:
        filters["search"] = search
    
    result = SessionService.get_program_sessions(
        db, program_id, skip=skip, limit=limit, filters=filters, sort_by=sort_by, sort_desc=sort_desc
    )
    
    return result

@router.get("/sessions/{session_id}", response_model=SessionDetailResponse)
def get_session(
    session_id: int,
    db: DbSession = Depends(get_db),
):
    """Get details of a specific session."""
    session = SessionService.get_session(db, session_id)
    return session

@router.put("/sessions/{session_id}", response_model=SessionResponse)
def update_session(
    session_id: int,
    session_data: SessionUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Update a session (trainer who created it or admin)."""
    session = SessionService.update_session(db, session_id, session_data, current_user)
    return session

@router.put("/sessions/{session_id}/cancel", response_model=SessionResponse)
def cancel_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Cancel a session (trainer who created it or admin)."""
    session = SessionService.cancel_session(db, session_id, current_user)
    return session

@router.get("/trainers/me/sessions", response_model=List[SessionResponse])
def get_my_sessions(
    is_cancelled: Optional[bool] = None,
    program_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_trainer_user),
    db: DbSession = Depends(get_db),
):
    """Get sessions created by the current trainer."""
    filters = {}
    
    if is_cancelled is not None:
        filters["is_cancelled"] = is_cancelled
        
    if program_id:
        filters["program_id"] = program_id
        
    if start_date:
        filters["start_date"] = datetime.combine(start_date, datetime.min.time())
        
    if end_date:
        filters["end_date"] = datetime.combine(end_date, datetime.max.time())
    
    sessions = SessionService.get_trainer_sessions(db, current_user.id, skip, limit, filters)
    return sessions