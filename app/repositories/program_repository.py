# File path: app/repositories/program_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from app.models.program import Program
from app.models.user import User

class ProgramRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> Program:
        """Create a new program in the database."""
        db_program = Program(**kwargs)
        db.add(db_program)
        db.commit()
        db.refresh(db_program)
        return db_program

    @staticmethod
    def get_by_id(db: Session, program_id: int) -> Optional[Program]:
        """Get a program by ID."""
        return db.query(Program).filter(Program.id == program_id).first()

    @staticmethod
    def update(db: Session, program: Program, **kwargs) -> Program:
        """Update a program's attributes."""
        for key, value in kwargs.items():
            if hasattr(program, key) and value is not None:
                setattr(program, key, value)
        
        db.commit()
        db.refresh(program)
        return program

    @staticmethod
    def delete(db: Session, program_id: int) -> bool:
        """Delete a program by ID."""
        program = db.query(Program).filter(Program.id == program_id).first()
        if program:
            db.delete(program)
            db.commit()
            return True
        return False

    @staticmethod
    def deactivate(db: Session, program_id: int) -> Optional[Program]:
        """Deactivate a program by ID."""
        program = db.query(Program).filter(Program.id == program_id).first()
        if program:
            program.is_active = False
            db.commit()
            db.refresh(program)
            return program
        return None

    @staticmethod
    def get_all(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> List[Program]:
        """Get all programs with filtering and sorting."""
        query = db.query(Program)
        
        # Apply filters
        if filters:
            if "category" in filters and filters["category"]:
                query = query.filter(Program.category == filters["category"])
            
            if "difficulty" in filters and filters["difficulty"]:
                query = query.filter(Program.difficulty == filters["difficulty"])
                
            if "is_active" in filters:
                query = query.filter(Program.is_active == filters["is_active"])
                
            if "created_by" in filters and filters["created_by"]:
                query = query.filter(Program.created_by == filters["created_by"])
                
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                query = query.filter(Program.name.ilike(search_term) | 
                                     Program.description.ilike(search_term))
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Program, sort_by)))
        else:
            query = query.order_by(asc(getattr(Program, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count(db: Session, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count programs with applied filters."""
        query = db.query(Program)
        
        # Apply filters
        if filters:
            if "category" in filters and filters["category"]:
                query = query.filter(Program.category == filters["category"])
            
            if "difficulty" in filters and filters["difficulty"]:
                query = query.filter(Program.difficulty == filters["difficulty"])
                
            if "is_active" in filters:
                query = query.filter(Program.is_active == filters["is_active"])
                
            if "created_by" in filters and filters["created_by"]:
                query = query.filter(Program.created_by == filters["created_by"])
                
            if "search" in filters and filters["search"]:
                search_term = f"%{filters['search']}%"
                query = query.filter(Program.name.ilike(search_term) | 
                                     Program.description.ilike(search_term))
        
        return query.count()

    @staticmethod
    def get_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Program]:
        """Get all programs created by a specific user."""
        return db.query(Program)\
            .filter(Program.created_by == user_id)\
            .offset(skip)\
            .limit(limit)\
            .all()