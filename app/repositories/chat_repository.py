from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.chatbot import ChatMessage

class ChatRepository:
    @staticmethod
    def create(db: Session, **kwargs) -> ChatMessage:
        """Create a new chat message in the database."""
        db_message = ChatMessage(**kwargs)
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message

    @staticmethod
    def get_by_user_id(db: Session, user_id: int, limit: int = 50) -> List[ChatMessage]:
        """Get recent chat messages for a user."""
        return db.query(ChatMessage)\
            .filter(ChatMessage.user_id == user_id)\
            .order_by(desc(ChatMessage.created_at))\
            .limit(limit)\
            .all()

    @staticmethod
    def count_by_user_id(db: Session, user_id: int) -> int:
        """Count chat messages for a user."""
        return db.query(ChatMessage)\
            .filter(ChatMessage.user_id == user_id)\
            .count()