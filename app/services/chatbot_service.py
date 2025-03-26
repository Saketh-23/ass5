from typing import List, Dict, Any
from sqlalchemy.orm import Session
from langchain_groq import ChatGroq

from app.models.user import User
from app.repositories.chat_repository import ChatRepository
from app.core.config import settings

class ChatbotService:
    @staticmethod
    def _get_chat_model():
        """Create and return a Groq chat model."""
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment variables")
            
        return ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name="llama3-70b-8192",
            temperature=0.7
        )

    @staticmethod
    def send_message(db: Session, user_message: str, user_id: int) -> Dict[str, Any]:
        """Process a user message and generate a response."""
        # Get recent conversation for context
        recent_messages = ChatRepository.get_by_user_id(db, user_id, limit=5)
        
        # Create chat history context
        conversation_history = ""
        for msg in reversed(recent_messages):  # Reverse to get chronological order
            prefix = "User: " if msg.is_user_message else "AI: "
            conversation_history += f"{prefix}{msg.content}\n\n"
        
        # Save user message
        user_msg = ChatRepository.create(
            db=db,
            user_id=user_id,
            is_user_message=True,
            content=user_message
        )
        
        # Setup the chat model
        chat = ChatbotService._get_chat_model()
        
        # Format messages directly for the model
        messages = [
            {"role": "system", "content": """
            You are ConnectFit AI, a fitness and wellness assistant.
            
            Your role is to provide helpful, accurate, and motivational advice on:
            - Fitness and workout recommendations
            - Nutrition and meal planning
            - Goal setting and tracking
            - General wellness tips
            
            Keep responses concise, informative, encouraging and supportive.
            If you don't know something, be honest about your limitations.
            Focus on evidence-based advice that promotes healthy and sustainable practices.
            
            Do not give specific medical advice and recommend consulting healthcare professionals when appropriate.
            """},
            {"role": "user", "content": f"""
            Previous conversation:
            {conversation_history}
            
            User: {user_message}
            """}
        ]
        
        # Generate response directly
        result = chat.invoke(messages)
        
        # Save AI response
        ai_msg = ChatRepository.create(
            db=db,
            user_id=user_id,
            is_user_message=False,
            content=result.content
        )
        
        return {
            "user_message": user_msg,
            "ai_response": ai_msg
        }

    @staticmethod
    def get_chat_history(db: Session, user_id: int, limit: int = 50) -> Dict[str, Any]:
        """Get chat history for a user."""
        messages = ChatRepository.get_by_user_id(db, user_id, limit)
        total = ChatRepository.count_by_user_id(db, user_id)
        
        # Return in chronological order (oldest first)
        return {
            "messages": list(reversed(messages)),
            "total": total
        }