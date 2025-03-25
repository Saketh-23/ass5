# File path: app/api/v1/endpoints/programs.py
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_current_trainer_user
from app.models.user import User
from app.models.enums import DifficultyLevel
from app.dto.request.program_dto import ProgramCreateRequest, ProgramUpdateRequest
from app.dto.response.program_dto import ProgramResponse, ProgramDetailResponse, ProgramListResponse
from app.services.program_service import ProgramService

router = APIRouter(prefix="/programs", tags=["Programs"])

@router.post("", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
def create_program(
    program_data: ProgramCreateRequest,
    current_user: User = Depends(get_current_trainer_user),
    db: Session = Depends(get_db),
):
    """Create a new program (trainer only)."""
    program = ProgramService.create_program(db, program_data, current_user)
    return program

@router.get("", response_model=ProgramListResponse)
def get_programs(
    category: Optional[str] = None,
    difficulty: Optional[DifficultyLevel] = None,
    is_active: bool = True,
    search: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    sort_by: str = Query("created_at", regex="^(name|category|difficulty|duration|created_at)$"),
    sort_desc: bool = True,
    db: Session = Depends(get_db),
):
    """Get all programs with filtering and sorting."""
    filters = {
        "category": category,
        "difficulty": difficulty,
        "is_active": is_active,
        "search": search,
    }
    
    result = ProgramService.get_programs(
        db, skip=skip, limit=limit, filters=filters, sort_by=sort_by, sort_desc=sort_desc
    )
    
    return result

@router.get("/my-programs", response_model=List[ProgramResponse])
def get_my_programs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_trainer_user),
    db: Session = Depends(get_db),
):
    """Get programs created by the current trainer."""
    programs = ProgramService.get_trainer_programs(db, current_user.id, skip, limit)
    return programs

@router.get("/{program_id}", response_model=ProgramDetailResponse)
def get_program(
    program_id: int,
    db: Session = Depends(get_db),
):
    """Get details of a specific program."""
    program = ProgramService.get_program(db, program_id)
    return program

@router.put("/{program_id}", response_model=ProgramResponse)
def update_program(
    program_id: int,
    program_data: ProgramUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a program (trainer who created it or admin)."""
    program = ProgramService.update_program(db, program_id, program_data, current_user)
    return program

@router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_program(
    program_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete/deactivate a program (trainer who created it or admin)."""
    ProgramService.delete_program(db, program_id, current_user)
    return None