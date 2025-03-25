# File path: app/services/discovery_service.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session as DbSession

from app.models.program import Program
from app.models.user import User
from app.repositories.program_repository import ProgramRepository

class DiscoveryService:
    @staticmethod
    def search_programs(
        db: DbSession,
        search_term: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 10,
        sort_by: str = "created_at",
        sort_desc: bool = True,
    ) -> Dict[str, Any]:
        """Search for programs with advanced filtering and sorting."""
        programs = ProgramRepository.search_programs(
            db, 
            search_term or "", 
            filters=filters, 
            skip=skip, 
            limit=limit, 
            sort_by=sort_by, 
            sort_desc=sort_desc
        )
        
        total = ProgramRepository.count_search_results(db, search_term or "", filters=filters)
        
        return {
            "items": programs,
            "total": total,
            "page": skip // limit + 1 if limit > 0 else 1,
            "size": limit,
            "pages": (total + limit - 1) // limit if limit > 0 else 1,
        }

    @staticmethod
    def get_featured_programs(db: DbSession, limit: int = 5) -> List[Program]:
        """Get featured or recommended programs."""
        return ProgramRepository.get_featured_programs(db, limit)

    @staticmethod
    def get_recommended_programs(db: DbSession, user_id: int, limit: int = 5) -> List[Program]:
        """Get personalized program recommendations for a user."""
        return ProgramRepository.get_recommended_programs(db, user_id, limit)
    
    @staticmethod
    def get_program_categories(db: DbSession) -> List[str]:
        """Get all unique program categories for filtering."""
        categories = db.query(Program.category).distinct().all()
        return [category[0] for category in categories]