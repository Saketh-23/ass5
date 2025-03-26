# app/core/scheduled_tasks.py

import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.goal_service import GoalService

logger = logging.getLogger(__name__)

def check_approaching_deadlines():
    """Check for goals with approaching deadlines and send notifications."""
    db = SessionLocal()
    try:
        logger.info("Running scheduled task: check_approaching_deadlines")
        GoalService.check_approaching_deadlines(db)
        logger.info("Completed scheduled task: check_approaching_deadlines")
    except Exception as e:
        logger.error(f"Error in scheduled task: {str(e)}")
    finally:
        db.close()

def setup_scheduled_tasks():
    """Set up scheduled tasks to run in the background."""
    scheduler = BackgroundScheduler()
    
    # Check approaching deadlines daily at 8 AM
    scheduler.add_job(
        check_approaching_deadlines,
        CronTrigger(hour=8, minute=0),
        id="check_approaching_deadlines",
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    logger.info("Scheduled tasks have been set up")
    
    return scheduler