# File path: app/api/v1/endpoints/discovery.py
from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session as DbSession

from app.core.database import get_db
from app.core.security import get_current_user, get_optional_user
from app.models.user import User
from app.models.enums import DifficultyLevel
from app.dto.response.program_dto import ProgramResponse, ProgramListResponse
from app.services.discovery_service import DiscoveryService

router = APIRouter(prefix="/discovery", tags=["Program Discovery"])

@router.get("/search", response_model=ProgramListResponse)
def search_programs(
    q: Optional[str] = None,
    category: Optional[str] = None,
    difficulty: Optional[DifficultyLevel] = None,
    min_duration: Optional[int] = Query(None, ge=1),
    max_duration: Optional[int] = Query(None, ge=1),
    trainer_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(name|category|difficulty|duration|created_at)$"),
    sort_desc: bool = True,
    db: DbSession = Depends(get_db),
):
    """
    Search for programs with advanced filtering and sorting.
    
    - **q**: Search term for program name, description, or trainer name
    - **category**: Filter by program category
    - **difficulty**: Filter by difficulty level
    - **min_duration**: Filter by minimum duration (in weeks)
    - **max_duration**: Filter by maximum duration (in weeks)
    - **trainer_id**: Filter by trainer ID
    - **skip**: Number of items to skip for pagination
    - **limit**: Maximum number of items to return
    - **sort_by**: Field to sort by
    - **sort_desc**: Sort in descending order if true
    """
    filters = {
        "category": category,
        "difficulty": difficulty,
        "min_duration": min_duration,
        "max_duration": max_duration,
        "trainer_id": trainer_id,
        "is_active": True,  # Only show active programs in search
    }
    
    result = DiscoveryService.search_programs(
        db, 
        search_term=q, 
        filters=filters, 
        skip=skip, 
        limit=limit, 
        sort_by=sort_by, 
        sort_desc=sort_desc
    )
    
    return result

@router.get("/featured", response_model=List[ProgramResponse])
def get_featured_programs(
    limit: int = Query(5, ge=1, le=20),
    db: DbSession = Depends(get_db),
):
    """
    Get featured or recommended programs.
    
    - **limit**: Maximum number of items to return
    """
    programs = DiscoveryService.get_featured_programs(db, limit)
    return programs

@router.get("/recommended", response_model=List[ProgramResponse])
def get_recommended_programs(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: DbSession = Depends(get_db),
):
    """
    Get personalized program recommendations.
    
    - **limit**: Maximum number of items to return
    """
    programs = DiscoveryService.get_recommended_programs(db, current_user.id, limit)
    return programs

@router.get("/categories", response_model=List[str])
def get_program_categories(
    db: DbSession = Depends(get_db),
):
    """Get all unique program categories for filtering."""
    categories = DiscoveryService.get_program_categories(db)
    return categories