# File path: app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, programs, sessions

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(programs.router)
api_router.include_router(sessions.router)

# Include additional routes here as they are created