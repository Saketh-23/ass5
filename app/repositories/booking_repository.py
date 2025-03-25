# File path: app/repositories/booking_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session as DbSession
from sqlalchemy import desc, asc
from datetime import datetime
from app.models.booking import Booking, BookingStatus

class BookingRepository:
    @staticmethod
    def create(db: DbSession, **kwargs) -> Booking:
        """Create a new booking in the database."""
        db_booking = Booking(**kwargs)
        db.add(db_booking)
        db.commit()
        db.refresh(db_booking)
        return db_booking

    @staticmethod
    def get_by_id(db: DbSession, booking_id: int) -> Optional[Booking]:
        """Get a booking by ID."""
        return db.query(Booking).filter(Booking.id == booking_id).first()

    @staticmethod
    def update(db: DbSession, booking: Booking, **kwargs) -> Booking:
        """Update a booking's attributes."""
        for key, value in kwargs.items():
            if hasattr(booking, key) and value is not None:
                setattr(booking, key, value)
        
        db.commit()
        db.refresh(booking)
        return booking

    @staticmethod
    def delete(db: DbSession, booking_id: int) -> bool:
        """Delete a booking by ID."""
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            db.delete(booking)
            db.commit()
            return True
        return False

    @staticmethod
    def cancel(db: DbSession, booking_id: int) -> Optional[Booking]:
        """Cancel a booking by ID."""
        booking = db.query(Booking).filter(Booking.id == booking_id).first()
        if booking:
            booking.status = BookingStatus.CANCELLED
            db.commit()
            db.refresh(booking)
            return booking
        return None

    @staticmethod
    def get_by_user_id(
        db: DbSession, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "booking_date",
        sort_desc: bool = True
    ) -> List[Booking]:
        """Get bookings by user ID with filtering and sorting."""
        query = db.query(Booking).filter(Booking.user_id == user_id)
        
        # Apply filters
        if filters:
            if "status" in filters and filters["status"]:
                query = query.filter(Booking.status == filters["status"])
                
            if "session_id" in filters and filters["session_id"]:
                query = query.filter(Booking.session_id == filters["session_id"])
                
            if "start_date" in filters and filters["start_date"]:
                query = query.filter(Booking.booking_date >= filters["start_date"])
                
            if "end_date" in filters and filters["end_date"]:
                query = query.filter(Booking.booking_date <= filters["end_date"])
                
            if "attended" in filters:
                query = query.filter(Booking.attended == filters["attended"])
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Booking, sort_by)))
        else:
            query = query.order_by(asc(getattr(Booking, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_by_user_id(
        db: DbSession, 
        user_id: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count bookings by user ID with applied filters."""
        query = db.query(Booking).filter(Booking.user_id == user_id)
        
        # Apply filters
        if filters:
            if "status" in filters and filters["status"]:
                query = query.filter(Booking.status == filters["status"])
                
            if "session_id" in filters and filters["session_id"]:
                query = query.filter(Booking.session_id == filters["session_id"])
                
            if "start_date" in filters and filters["start_date"]:
                query = query.filter(Booking.booking_date >= filters["start_date"])
                
            if "end_date" in filters and filters["end_date"]:
                query = query.filter(Booking.booking_date <= filters["end_date"])
                
            if "attended" in filters:
                query = query.filter(Booking.attended == filters["attended"])
                
        return query.count()

    @staticmethod
    def get_by_session_id(
        db: DbSession, 
        session_id: int, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Booking]:
        """Get bookings by session ID with filtering."""
        query = db.query(Booking).filter(Booking.session_id == session_id)
        
        # Apply filters
        if filters:
            if "status" in filters and filters["status"]:
                query = query.filter(Booking.status == filters["status"])
                
            if "user_id" in filters and filters["user_id"]:
                query = query.filter(Booking.user_id == filters["user_id"])
                
            if "attended" in filters:
                query = query.filter(Booking.attended == filters["attended"])
                
        return query.order_by(asc(Booking.booking_date)).offset(skip).limit(limit).all()

    @staticmethod
    def count_by_session_id(
        db: DbSession, 
        session_id: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count bookings by session ID with applied filters."""
        query = db.query(Booking).filter(Booking.session_id == session_id)
        
        # Apply filters
        if filters:
            if "status" in filters and filters["status"]:
                query = query.filter(Booking.status == filters["status"])
                
            if "user_id" in filters and filters["user_id"]:
                query = query.filter(Booking.user_id == filters["user_id"])
                
            if "attended" in filters:
                query = query.filter(Booking.attended == filters["attended"])
                
        return query.count()