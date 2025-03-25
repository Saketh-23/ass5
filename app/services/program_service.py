# File path: app/services/program_service.py
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.program import Program
from app.dto.request.program_dto import ProgramCreateRequest, ProgramUpdateRequest
from app.repositories.program_repository import ProgramRepository
from app.models.user import User, UserRole

class ProgramService:
    @staticmethod
    def create_program(db: Session, program_data: ProgramCreateRequest, user: User) -> Program:
        """Create a new program."""
        # Check if user is a trainer or admin
        if user.role not in [UserRole.TRAINER, UserRole.ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only trainers and admins can create programs",
            )
        
        # Create the program
        return ProgramRepository.create(
            db=db,
            name=program_data.name,
            description=program_data.description,
            category=program_data.category,
            difficulty=program_data.difficulty,
            duration=program_data.duration,
            created_by=user.id,
            image_url=program_data.image_url,
        )

    @staticmethod
    def get_program(db: Session, program_id: int) -> Program:
        """Get a program by ID with rating information."""
        program = ProgramRepository.get_by_id(db, program_id)
        if not program:
            raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Program not found",
            )
    
    # Get program rating
        from app.repositories.review_repository import ReviewRepository
        avg_rating, review_count = ReviewRepository.get_program_rating(db, program_id)
    
    # Attach rating information to the program
        program.average_rating = avg_rating
        program.total_reviews = review_count
    
        return program

    @staticmethod
    def update_program(
        db: Session, program_id: int, program_data: ProgramUpdateRequest, user: User
    ) -> Program:
        """Update a program."""
        # Get the program
        program = ProgramService.get_program(db, program_id)
        
        # Check if user is the creator or an admin
        if program.created_by != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the creator or an admin can update this program",
            )
        
        # Update the program
        return ProgramRepository.update(
            db=db,
            program=program,
            name=program_data.name,
            description=program_data.description,
            category=program_data.category,
            difficulty=program_data.difficulty,
            duration=program_data.duration,
            is_active=program_data.is_active,
            image_url=program_data.image_url,
        )

    @staticmethod
    def delete_program(db: Session, program_id: int, user: User) -> bool:
        """Delete or deactivate a program."""
        # Get the program
        program = ProgramService.get_program(db, program_id)
        
        # Check if user is the creator or an admin
        if program.created_by != user.id and user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the creator or an admin can delete this program",
            )
        
        # Admin can fully delete, others just deactivate
        if user.role == UserRole.ADMIN:
            return ProgramRepository.delete(db, program_id)
        else:
            program = ProgramRepository.deactivate(db, program_id)
            return program is not None

    @staticmethod
    def get_programs(
        db: Session,
        skip: int = 0,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Get all programs with pagination, filtering, and sorting."""
        programs = ProgramRepository.get_all(
            db, skip=skip, limit=limit, filters=filters, sort_by=sort_by, sort_desc=sort_desc
        )
        
        total = ProgramRepository.count(db, filters=filters)
        
        return {
            "items": programs,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def get_trainer_programs(
        db: Session, user_id: int, skip: int = 0, limit: int = 10
    ) -> List[Program]:
        """Get all programs created by a specific trainer."""
        return ProgramRepository.get_by_user_id(db, user_id, skip, limit)