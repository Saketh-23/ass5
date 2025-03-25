# File path: app/api/v1/endpoints/bookings.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as DbSession
from datetime import datetime, date

from app.core.database import get_db
from app.core.security import get_current_user, get_current_trainer_user
from app.models.user import User
from app.models.booking import BookingStatus
from app.dto.request.booking_dto import BookingCreateRequest, BookingUpdateRequest
from app.dto.response.booking_dto import BookingResponse, BookingDetailResponse, BookingListResponse
from app.services.booking_service import BookingService

router = APIRouter()

@router.post("/sessions/{session_id}/bookings", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
def book_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Book a session."""
    booking_data = BookingCreateRequest(session_id=session_id)
    booking = BookingService.create_booking(db, booking_data, current_user)
    return booking

@router.get("/bookings/{booking_id}", response_model=BookingDetailResponse)
def get_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get details of a specific booking."""
    booking = BookingService.get_booking(db, booking_id)
    
    # Check if user is authorized to view this booking
    is_owner = booking.user_id == current_user.id
    is_session_trainer = booking.session.trainer_id == current_user.id
    is_admin = current_user.role == "ADMIN"
    
    if not (is_owner or is_session_trainer or is_admin):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to view this booking",
        )
    
    return booking

@router.put("/bookings/{booking_id}/cancel", response_model=BookingResponse)
def cancel_booking(
    booking_id: int,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Cancel a booking."""
    booking = BookingService.cancel_booking(db, booking_id, current_user)
    return booking

@router.put("/bookings/{booking_id}/attendance", response_model=BookingResponse)
def update_attendance(
    booking_id: int,
    attended: bool,
    current_user: User = Depends(get_current_trainer_user),
    db: DbSession = Depends(get_db),
):
    """Update attendance for a booking (trainer only)."""
    booking = BookingService.update_booking_attendance(db, booking_id, attended, current_user)
    return booking

@router.get("/users/me/bookings", response_model=BookingListResponse)
def get_my_bookings(
    status: Optional[BookingStatus] = None,
    session_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    attended: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("booking_date", regex="^(booking_date|created_at|status)$"),
    sort_desc: bool = True,
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """Get current user's bookings."""
    filters = {}
    
    if status:
        filters["status"] = status
        
    if session_id:
        filters["session_id"] = session_id
        
    if start_date:
        filters["start_date"] = datetime.combine(start_date, datetime.min.time())
        
    if end_date:
        filters["end_date"] = datetime.combine(end_date, datetime.max.time())
        
    if attended is not None:
        filters["attended"] = attended
    
    result = BookingService.get_user_bookings(
        db, current_user.id, skip=skip, limit=limit, filters=filters, sort_by=sort_by, sort_desc=sort_desc
    )
    
    return result

@router.get("/sessions/{session_id}/bookings", response_model=BookingListResponse)
def get_session_bookings(
    session_id: int,
    status: Optional[BookingStatus] = None,
    attended: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_trainer_user),
    db: DbSession = Depends(get_db),
):
    """Get bookings for a specific session (trainer only)."""
    filters = {}
    
    if status:
        filters["status"] = status
        
    if attended is not None:
        filters["attended"] = attended
    
    result = BookingService.get_session_bookings(
        db, session_id, skip=skip, limit=limit, filters=filters
    )
    
    return result