from typing import Dict, Any, Optional
from langchain_groq import ChatGroq
import json
import re

from app.core.config import settings

class AIService:
    @staticmethod
    def _get_chat_model():
        """Create and return a Groq chat model."""
        if not settings.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in environment variables")
            
        return ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model_name="llama3-70b-8192",
            temperature=0.2
        )

    @staticmethod
    def analyze_meal_nutrition(meal_name: str, meal_description: Optional[str] = None) -> Dict[str, Any]:
        """Analyze nutrition content of a meal using LLM."""
        try:
            # Check if we have valid input
            if not meal_name and not meal_description:
                print("Warning: Both meal name and description are empty")
                return {
                    "calories": 300,
                    "protein": 10.0,
                    "carbs": 30.0,
                    "fat": 10.0,
                    "analysis_details": "No meal information provided."
                }
                
            # Check API key
            if not settings.GROQ_API_KEY:
                print("Error: GROQ_API_KEY is not set")
                return {
                    "calories": 300,
                    "protein": 10.0,
                    "carbs": 30.0,
                    "fat": 10.0,
                    "analysis_details": "API key not configured properly."
                }
            
            chat = AIService._get_chat_model()
            
            print(f"Analyzing meal: {meal_name}, Description: {meal_description or 'None'}")
            
            # Format messages directly for the model
            messages = [
                {"role": "system", "content": """
                You are a nutrition expert that analyzes meals and estimates their nutrition content.
                Provide your response as a JSON object with the following keys:
                - calories: total calories (integer)
                - protein: protein in grams (float)
                - carbs: carbohydrates in grams (float) 
                - fat: fat in grams (float)
                - analysis_details: brief description of main nutrients/ingredients
                
                Make sure to format your response as valid JSON.
                """},
                {"role": "user", "content": f"""
                Meal name: {meal_name}
                Description: {meal_description or ""}
                
                Please provide a nutritional analysis.
                """}
            ]
            
            # Generate response directly
            print("Sending request to Groq API")
            result = chat.invoke(messages)
            print(f"Received response: {result.content[:100]}...")
            
            # Extract JSON from the response
            content = result.content
            # Look for JSON in the response
            json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL) or re.search(r'\{.*\}', content, re.DOTALL)
            
            if json_match:
                extracted_json = json_match.group(1) if '```json' in content else json_match.group(0)
                print(f"Extracted JSON: {extracted_json[:100]}...")
                
                parsed_data = json.loads(extracted_json)
                print(f"Successfully parsed JSON: {list(parsed_data.keys())}")
                return parsed_data
            else:
                print(f"No JSON found in response. Response starts with: {content[:100]}")
                return {
                    "calories": 300,
                    "protein": 10.0,
                    "carbs": 30.0,
                    "fat": 10.0,
                    "analysis_details": "Could not extract structured data from response."
                }
        except Exception as e:
            print(f"Error analyzing meal: {str(e)}")
            import traceback
            traceback.print_exc()
            
            # Fallback to a basic estimation if any error occurs
            return {
                "calories": 300,
                "protein": 10.0,
                "carbs": 30.0,
                "fat": 10.0,
                "analysis_details": f"Error during analysis: {str(e)[:100]}"
            }

    @staticmethod
    def generate_diet_plan(user_input: str) -> Dict[str, Any]:
        """Generate a diet plan based on user's natural language input."""
        chat = AIService._get_chat_model()
        
        # Format messages directly for the model
        messages = [
            {"role": "system", "content": """
            You are a nutrition expert that creates personalized meal plans.
            The user will describe their goals and preferences, and you will generate a 7-day meal plan.
            
            Your meal plan should include:
            1. Breakfast, lunch, dinner, and optional snacks for each day
            2. Estimated calories for each meal
            3. A brief overview of the nutritional approach
            
            Provide your response in a clear, structured format that's easy to read.
            """},
            {"role": "user", "content": f"""
            Please create a meal plan based on the following request:
            
            {user_input}
            """}
        ]
        
        # Generate response directly
        result = chat.invoke(messages)
        
        return {
            "diet_plan": result.content,
            "request": user_input
        }

    @staticmethod
    def get_workout_recommendation(user_input: str) -> Dict[str, Any]:
        """Generate a workout recommendation based on user's natural language input."""
        chat = AIService._get_chat_model()
        
        # Format messages directly for the model
        messages = [
            {"role": "system", "content": """
            You are a fitness expert that creates personalized workout plans.
            The user will describe their goals, fitness level, and preferences, and you will generate a workout plan.
            
            Your workout plan should include:
            1. Training schedule (days per week)
            2. Specific exercises with sets, reps, and rest periods
            3. Progression guidelines
            4. Safety tips
            
            Provide your response in a clear, structured format that's easy to read.
            """},
            {"role": "user", "content": f"""
            Please create a workout plan based on the following request:
            
            {user_input}
            """}
        ]
        
        # Generate response directly
        result = chat.invoke(messages)
        
        return {
            "workout_plan": result.content,
            "request": user_input
        }