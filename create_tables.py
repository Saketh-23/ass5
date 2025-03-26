# create_tables.py
from app.models.base import Base
from app.core.database import engine

# Import all models
from app.models.user import User
from app.models.program import Program
from app.models.session import Session
from app.models.booking import Booking
from app.models.goal import Goal
from app.models.progress import Progress
from app.models.achievement import Achievement
from app.models.notification import Notification
from app.models.forum import Forum
from app.models.forum_membership import ForumMembership
from app.models.discussion import Discussion
from app.models.comment import Comment
from app.models.like import Like
from app.models.review import Review

# Create all tables
def main():
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully.")

if __name__ == "__main__":
    main()