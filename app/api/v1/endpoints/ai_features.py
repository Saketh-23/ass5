from typing import Dict, Any, List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.dto.request.ai_dto import ChatMessageRequest, DietPlanRequest, WorkoutPlanRequest
from app.dto.response.ai_dto import ChatMessageResponse, ChatHistoryResponse, DietPlanResponse, WorkoutPlanResponse
from app.services.chatbot_service import ChatbotService
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI Features"])

@router.post("/chat", response_model=Dict[str, Any])
def chat_with_ai(
   request: ChatMessageRequest,
   current_user: User = Depends(get_current_user),
   db: Session = Depends(get_db),
):
   """Chat with the AI assistant."""
   response = ChatbotService.send_message(
       db, 
       request.message, 
       current_user.id
   )
   
   return {
       "user_message": {
           "id": response["user_message"].id,
           "is_user_message": response["user_message"].is_user_message,
           "content": response["user_message"].content,
           "created_at": response["user_message"].created_at
       },
       "ai_response": {
           "id": response["ai_response"].id,
           "is_user_message": response["ai_response"].is_user_message,
           "content": response["ai_response"].content,
           "created_at": response["ai_response"].created_at
       }
   }

@router.get("/chat-history", response_model=ChatHistoryResponse)
def get_chat_history(
   current_user: User = Depends(get_current_user),
   db: Session = Depends(get_db),
):
   """Get the user's chat history."""
   history = ChatbotService.get_chat_history(db, current_user.id)
   return history

@router.post("/diet-plan", response_model=DietPlanResponse)
def generate_diet_plan(
   request: DietPlanRequest,
   current_user: User = Depends(get_current_user),
):
   """Generate a personalized diet plan based on user input."""
   diet_plan = AIService.generate_diet_plan(request.user_input)
   return diet_plan

@router.post("/workout-plan", response_model=WorkoutPlanResponse)
def generate_workout_plan(
   request: WorkoutPlanRequest,
   current_user: User = Depends(get_current_user),
):
   """Generate a personalized workout plan based on user input."""
   workout_plan = AIService.get_workout_recommendation(request.user_input)
   return workout_plan