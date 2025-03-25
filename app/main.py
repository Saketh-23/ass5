# File path: app/main.py
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.v1.router import api_router
from app.core.config import settings
from app.models.base import Base
from app.core.database import engine, get_db
from app.core.init_db import init_db

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

# Create database tables at startup
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
    db = next(get_db())
    try:
        init_db(db)
    finally:
        db.close()

@app.get("/")
def root():
    return {"message": f"Welcome to {settings.APP_NAME} API. Visit /docs for documentation."}