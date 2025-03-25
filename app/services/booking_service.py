# File path: app/services/booking_service.py
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DbSession
from datetime import datetime

from app.models.booking import Booking, BookingStatus
from app.models.session import Session
from app.models.user import User, UserRole
from app.dto.request.booking_dto import BookingCreateRequest, BookingUpdateRequest
from app.repositories.booking_repository import BookingRepository
from app.repositories.session_repository import SessionRepository

class BookingService:
    @staticmethod
    def create_booking(db: DbSession, booking_data: BookingCreateRequest, user: User) -> Booking:
        """Book a session for the user."""
        # Check if session exists
        session = SessionRepository.get_by_id(db, booking_data.session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {booking_data.session_id} not found",
            )
        
        # Check if session is not cancelled
        if session.is_cancelled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book a cancelled session",
            )
        
        # Check if session has available slots
        if session.available_slots <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Session is fully booked",
            )
        
        # Check if user already has a booking for this session
        existing_booking = db.query(Booking).filter(
            Booking.user_id == user.id,
            Booking.session_id == booking_data.session_id,
            Booking.status != BookingStatus.CANCELLED
        ).first()
        
        if existing_booking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already have a booking for this session",
            )
        
        # Create the booking
        booking = BookingRepository.create(
            db=db,
            user_id=user.id,
            session_id=booking_data.session_id,
            status=BookingStatus.CONFIRMED,  # Auto-confirm for now, could be PENDING if payment is required
            attended=False,
        )
        
        # Update available slots in session
        session.available_slots -= 1
        db.commit()
        
        return booking

    @staticmethod
    def get_booking(db: DbSession, booking_id: int) -> Booking:
        """Get a booking by ID."""
        booking = BookingRepository.get_by_id(db, booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )
        return booking

    @staticmethod
    def cancel_booking(db: DbSession, booking_id: int, user: User) -> Booking:
        """Cancel a booking."""
        # Get the booking
        booking = BookingService.get_booking(db, booking_id)
        
        # Check if booking belongs to user or user is admin/trainer
        is_owner = booking.user_id == user.id
        is_session_trainer = booking.session.trainer_id == user.id
        is_admin = user.role == UserRole.ADMIN
        
        if not (is_owner or is_session_trainer or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to cancel this booking",
            )
        
        # Check if booking is already cancelled
        if booking.status == BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is already cancelled",
            )
        
        # Cancel the booking
        cancelled_booking = BookingRepository.cancel(db, booking_id)
        if not cancelled_booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found",
            )
        
        # Increment available slots in session
        session = SessionRepository.get_by_id(db, booking.session_id)
        if session and not session.is_cancelled:
            session.available_slots += 1
            db.commit()
        
        return cancelled_booking

    @staticmethod
    def update_booking_attendance(
        db: DbSession, booking_id: int, attended: bool, user: User
    ) -> Booking:
        """Update a booking's attendance status (trainers only)."""
        # Get the booking
        booking = BookingService.get_booking(db, booking_id)
        
        # Check if user is the session's trainer or an admin
        is_session_trainer = booking.session.trainer_id == user.id
        is_admin = user.role == UserRole.ADMIN
        
        if not (is_session_trainer or is_admin):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the session trainer or an admin can update attendance",
            )
        
        # Update the booking
        return BookingRepository.update(
            db=db,
            booking=booking,
            attended=attended,
        )

    @staticmethod
    def get_user_bookings(
        db: DbSession,
        user_id: int,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "booking_date",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Get all bookings for a user with pagination, filtering, and sorting."""
        bookings = BookingRepository.get_by_user_id(
            db, user_id, skip=skip, limit=limit, filters=filters, sort_by=sort_by, sort_desc=sort_desc
        )
        
        total = BookingRepository.count_by_user_id(db, user_id, filters=filters)
        
        return {
            "items": bookings,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def get_session_bookings(
        db: DbSession,
        session_id: int,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get all bookings for a session with pagination and filtering."""
        # Check if session exists
        session = SessionRepository.get_by_id(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session with ID {session_id} not found",
            )
        
        bookings = BookingRepository.get_by_session_id(
            db, session_id, skip=skip, limit=limit, filters=filters
        )
        
        total = BookingRepository.count_by_session_id(db, session_id, filters=filters)
        
        return {
            "items": bookings,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }