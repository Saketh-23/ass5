from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    get_current_user, 
    get_current_active_user, 
    get_current_admin_user, 
    get_current_trainer_user
)

# Export common dependencies for reuse across endpoints