# File path: app/repositories/program_repository.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc, or_
from app.models.program import Program
from app.models.user import User
from app.models.booking import Booking
from app.models.session import Session

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

    @staticmethod
    def search_programs(
        db: Session, 
        search_term: str,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0, 
        limit: int = 10,
        sort_by: str = "created_at",
        sort_desc: bool = True
    ) -> List[Program]:
        """Search programs by name, description, or trainer name."""
        # Join with User to search by trainer name
        query = db.query(Program).join(User, Program.created_by == User.id)
        
        # Apply search term
        if search_term:
            search_term = f"%{search_term}%"
            query = query.filter(
                or_(
                    Program.name.ilike(search_term),
                    Program.description.ilike(search_term),
                    User.username.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term)
                )
            )
        
        # Apply additional filters
        if filters:
            if "category" in filters and filters["category"]:
                query = query.filter(Program.category == filters["category"])
                
            if "difficulty" in filters and filters["difficulty"]:
                query = query.filter(Program.difficulty == filters["difficulty"])
                
            if "min_duration" in filters and filters["min_duration"]:
                query = query.filter(Program.duration >= filters["min_duration"])
                
            if "max_duration" in filters and filters["max_duration"]:
                query = query.filter(Program.duration <= filters["max_duration"])
                
            if "trainer_id" in filters and filters["trainer_id"]:
                query = query.filter(Program.created_by == filters["trainer_id"])
                
            if "is_active" in filters:
                query = query.filter(Program.is_active == filters["is_active"])
        
        # Apply sorting
        if sort_desc:
            query = query.order_by(desc(getattr(Program, sort_by)))
        else:
            query = query.order_by(asc(getattr(Program, sort_by)))
            
        # Apply pagination
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def count_search_results(
        db: Session, 
        search_term: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> int:
        """Count the number of programs matching search and filter criteria."""
        # Join with User to search by trainer name
        query = db.query(Program).join(User, Program.created_by == User.id)
        
        # Apply search term
        if search_term:
            search_term = f"%{search_term}%"
            query = query.filter(
                or_(
                    Program.name.ilike(search_term),
                    Program.description.ilike(search_term),
                    User.username.ilike(search_term),
                    User.first_name.ilike(search_term),
                    User.last_name.ilike(search_term)
                )
            )
        
        # Apply additional filters
        if filters:
            if "category" in filters and filters["category"]:
                query = query.filter(Program.category == filters["category"])
                
            if "difficulty" in filters and filters["difficulty"]:
                query = query.filter(Program.difficulty == filters["difficulty"])
                
            if "min_duration" in filters and filters["min_duration"]:
                query = query.filter(Program.duration >= filters["min_duration"])
                
            if "max_duration" in filters and filters["max_duration"]:
                query = query.filter(Program.duration <= filters["max_duration"])
                
            if "trainer_id" in filters and filters["trainer_id"]:
                query = query.filter(Program.created_by == filters["trainer_id"])
                
            if "is_active" in filters:
                query = query.filter(Program.is_active == filters["is_active"])
        
        return query.count()

    @staticmethod
    def get_featured_programs(db: Session, limit: int = 5) -> List[Program]:
        """Get featured or recommended programs based on criteria."""
        # For now, simply get the most recently created active programs
        # Later this could be enhanced with popularity metrics, ratings, etc.
        return db.query(Program)\
            .filter(Program.is_active == True)\
            .order_by(desc(Program.created_at))\
            .limit(limit)\
            .all()

    @staticmethod
    def get_recommended_programs(
        db: Session, 
        user_id: int,
        limit: int = 5
    ) -> List[Program]:
        """
        Get personalized program recommendations for a user.
        
        This is a simple implementation that recommends programs 
        based on the user's booking history categories and difficulties.
        """
        # Find categories and difficulties the user has booked before
        user_bookings = db.query(Booking).filter(Booking.user_id == user_id).all()
        
        if not user_bookings:
            # If no booking history, return featured programs
            return ProgramRepository.get_featured_programs(db, limit)
        
        # Get session IDs from bookings
        session_ids = [booking.session_id for booking in user_bookings]
        
        # Get sessions
        sessions = db.query(Session).filter(Session.id.in_(session_ids)).all()
        
        # Get program IDs from sessions
        program_ids = [session.program_id for session in sessions]
        
        # Get programs
        booked_programs = db.query(Program).filter(Program.id.in_(program_ids)).all()
        
        # Extract categories and difficulties
        categories = set(program.category for program in booked_programs)
        difficulties = set(program.difficulty for program in booked_programs)
        
        # Find similar programs the user hasn't booked yet
        query = db.query(Program)\
            .filter(Program.is_active == True)\
            .filter(Program.id.notin_(program_ids))
        
        if categories:
            query = query.filter(Program.category.in_(categories))
        
        if difficulties:
            query = query.filter(Program.difficulty.in_(difficulties))
        
        return query.order_by(desc(Program.created_at)).limit(limit).all()