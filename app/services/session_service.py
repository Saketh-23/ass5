# File path: app/services/session_service.py
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session as DbSession
from datetime import datetime

from app.models.session import Session
from app.models.user import User, UserRole
from app.dto.request.session_dto import SessionCreateRequest, SessionUpdateRequest
from app.repositories.session_repository import SessionRepository
from app.repositories.program_repository import ProgramRepository

class SessionService:
    @staticmethod
    def create_session(db: DbSession, session_data: SessionCreateRequest, user: User) -> Session:
        """Create a new session."""
        # Check if user is a trainer or admin
        if user.role not in [UserRole.TRAINER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only trainers and admins can create sessions",
            )
        
        # Check if program exists
        program = ProgramRepository.get_by_id(db, session_data.program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {session_data.program_id} not found",
            )
        
        # Check if user is the program creator or an admin
        if program.created_by != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create sessions for your own programs",
            )
        
        # Create the session
        return SessionRepository.create(
            db=db,
            program_id=session_data.program_id,
            trainer_id=user.id,
            title=session_data.title,
            description=session_data.description,
            start_time=session_data.start_time,
            end_time=session_data.end_time,
            total_slots=session_data.total_slots,
            available_slots=session_data.total_slots,  # Initially all slots are available
            price=session_data.price,
            location=session_data.location,
            is_virtual=session_data.is_virtual,
            meeting_link=session_data.meeting_link,
        )

    @staticmethod
    def get_session(db: DbSession, session_id: int) -> Session:
        """Get a session by ID."""
        session = SessionRepository.get_by_id(db, session_id)
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        return session

    @staticmethod
    def update_session(
        db: DbSession, session_id: int, session_data: SessionUpdateRequest, user: User
    ) -> Session:
        """Update a session."""
        # Get the session
        session = SessionService.get_session(db, session_id)
        
        # Check if user is the trainer or an admin
        if session.trainer_id != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the trainer or an admin can update this session",
            )
        
        # Update the session
        return SessionRepository.update(
            db=db,
            session=session,
            title=session_data.title,
            description=session_data.description,
            start_time=session_data.start_time,
            end_time=session_data.end_time,
            total_slots=session_data.total_slots,
            price=session_data.price,
            location=session_data.location,
            is_virtual=session_data.is_virtual,
            meeting_link=session_data.meeting_link,
        )

    @staticmethod
    def cancel_session(db: DbSession, session_id: int, user: User) -> Session:
        """Cancel a session."""
        # Get the session
        session = SessionService.get_session(db, session_id)
        
        # Check if user is the trainer or an admin
        if session.trainer_id != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the trainer or an admin can cancel this session",
            )
        
        # Cancel the session
        cancelled_session = SessionRepository.cancel(db, session_id)
        if not cancelled_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found",
            )
        return cancelled_session

    @staticmethod
    def get_program_sessions(
        db: DbSession,
        program_id: int,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "start_time",
        sort_desc: bool = False,
    ) -> Dict[str, Any]:
        """Get all sessions for a program with pagination, filtering, and sorting."""
        # Check if program exists
        program = ProgramRepository.get_by_id(db, program_id)
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {program_id} not found",
            )
        
        sessions = SessionRepository.get_by_program_id(
            db, program_id, skip=skip, limit=limit, filters=filters, sort_by=sort_by, sort_desc=sort_desc
        )
        
        total = SessionRepository.count_by_program_id(db, program_id, filters=filters)
        
        return {
            "items": sessions,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def get_trainer_sessions(
        db: DbSession, user_id: int, skip: int = 0, limit: int = 10, filters: Optional[Dict[str, Any]] = None
    ) -> List[Session]:
        """Get all sessions for a trainer."""
        return SessionRepository.get_by_trainer_id(db, user_id, skip, limit, filters)