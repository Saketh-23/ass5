# File path: app/repositories/session_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session as DbSession
from sqlalchemy import desc, asc
from app.models.session import Session

class SessionRepository:
    @staticmethod
    def create(db: DbSession, **kwargs) -> Session:
        """Create a new session in the database."""
        # Set available_slots equal to total_slots initially
        if 'total_slots' in kwargs and 'available_slots' not in kwargs:
            kwargs['available_slots'] = kwargs['total_slots']
            
        db_session = Session(**kwargs)
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session

    @staticmethod
    def get_by_id(db: DbSession, session_id: int) -> Optional[Session]:
        """Get a session by ID."""
        return db.query(Session).filter(Session.id == session_id).first()

    @staticmethod
    def update(db: DbSession, session: Session, **kwargs) -> Session:
        """Update a session's attributes."""
        # If total_slots changes, adjust available_slots accordingly
        if 'total_slots' in kwargs and kwargs['total_slots'] is not None:
            current_available = session.available_slots
            current_total = session.total_slots
            new_total = kwargs['total_slots']
            
            # Calculate the difference in booked slots
            booked_slots = current_total - current_available
            
            # Ensure we don't set available_slots to less than 0
            new_available = max(0, new_total - booked_slots)
            kwargs['available_slots'] = new_available
        
        for key, value in kwargs.items():
            if hasattr(session, key) and value is not None:
                setattr(session, key, value)
        
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def delete(db: DbSession, session_id: int) -> bool:
        """Delete a session by ID."""
        session = db.query(Session).filter(Session.id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False

    @staticmethod
    def cancel(db: DbSession, session_id: int) -> Optional[Session]:
        """Cancel a session by ID."""
        session = db.query(Session).filter(Session.id == session_id).first()
        if session:
            session.is_cancelled = True
            db.commit()
            db.refresh(session)
            return session
        return None

    @staticmethod
    def get_by_program_id(
        db: DbSession, 
        program_id: int, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "start_time",
        sort_desc: bool = False
    ) -> List[Session]:
        """Get sessions by program ID with filtering and sorting."""
        query = db.query(Session).filter(Session.program_id == program_id)
        
        # Apply filters
        if filters:
            if "is_cancelled" in filters:
                query = query.filter(Session.is_cancelled == filters["is_cancelled"])
                
            if "trainer_id" in filters and filters["trainer_id"]:
                query = query.filter(Session.trainer_id == filters["trainer_id"])
                
            if "start_date" in filters and filters["start_date"]:
                query = query.filter(Session.start_time >= filters["start_date"])
                
            if "end_date" in filters and filters["end_date"]:
                query = query.filter(Session.end_time <= filters["end_date"])
                
            if "has_available_slots" in filters and filters["has_available_slots"]:
                query = query.filter(Session.available_slots > 0)
                
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                query = query.filter(Session.title.ilike(search_term) | 
                                     Session.description.ilike(search_term))
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Session, sort_by)))
        else:
            query = query.order_by(asc(getattr(Session, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_by_program_id(
        db: DbSession, 
        program_id: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count sessions by program ID with applied filters."""
        query = db.query(Session).filter(Session.program_id == program_id)
        
        # Apply filters
        if filters:
            if "is_cancelled" in filters:
                query = query.filter(Session.is_cancelled == filters["is_cancelled"])
                
            if "trainer_id" in filters and filters["trainer_id"]:
                query = query.filter(Session.trainer_id == filters["trainer_id"])
                
            if "start_date" in filters and filters["start_date"]:
                query = query.filter(Session.start_time >= filters["start_date"])
                
            if "end_date" in filters and filters["end_date"]:
                query = query.filter(Session.end_time <= filters["end_date"])
                
            if "has_available_slots" in filters and filters["has_available_slots"]:
                query = query.filter(Session.available_slots > 0)
                
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                query = query.filter(Session.title.ilike(search_term) | 
                                     Session.description.ilike(search_term))
                
        return query.count()

    @staticmethod
    def get_by_trainer_id(
        db: DbSession, 
        trainer_id: int, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Session]:
        """Get sessions by trainer ID with filtering."""
        query = db.query(Session).filter(Session.trainer_id == trainer_id)
        
        # Apply filters (similar to get_by_program_id)
        if filters:
            if "is_cancelled" in filters:
                query = query.filter(Session.is_cancelled == filters["is_cancelled"])
                
            if "program_id" in filters and filters["program_id"]:
                query = query.filter(Session.program_id == filters["program_id"])
                
            if "start_date" in filters and filters["start_date"]:
                query = query.filter(Session.start_time >= filters["start_date"])
                
            if "end_date" in filters and filters["end_date"]:
                query = query.filter(Session.end_time <= filters["end_date"])
                
            if "has_available_slots" in filters and filters["has_available_slots"]:
                query = query.filter(Session.available_slots > 0)
                
        return query.order_by(asc(Session.start_time)).offset(skip).limit(limit).all()