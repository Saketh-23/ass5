# File path: app/api/v1/router.py
from fastapi import APIRouter

from app.api.v1.endpoints import (
    auth, meals, users, programs, sessions, bookings, discovery, 
    reviews, forums, memberships, discussions, comments, likes,
    goals, progress, achievements, notifications,ai_features 
)

api_router = APIRouter()

# Include existing routers
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
api_router.include_router(comments.router)
api_router.include_router(likes.router)

# Include new routers for goals, progress, achievements, and notifications
api_router.include_router(goals.router)
api_router.include_router(progress.router)
api_router.include_router(achievements.router)
api_router.include_router(notifications.router)
api_router.include_router(ai_features.router) 
api_router.include_router(meals.router)
