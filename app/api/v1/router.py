# File path: app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.endpoints import auth, users, programs, sessions, bookings, discovery, reviews, forums, memberships, discussions

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(programs.router)
api_router.include_router(sessions.router)
api_router.include_router(bookings.router)
api_router.include_router(discovery.router)
api_router.include_router(reviews.router)
api_router.include_router(forums.router)
api_router.include_router(memberships.router)
api_router.include_router(discussions.router)

# Include additional routes here as they are created