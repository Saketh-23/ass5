# app/services/progress_assessment_service.py

from typing import Dict, Any, Optional, List, Tuple
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import numpy as np
from scipy import stats

from app.models.user import User
from app.models.goal import Goal, GoalStatus
from app.repositories.goal_repository import GoalRepository
from app.repositories.progress_repository import ProgressRepository

class ProgressAssessmentService:
    @staticmethod
    def assess_goal_progress(db: Session, goal_id: int, user_id: int) -> Dict[str, Any]:
        """Assess progress for a specific goal."""
        # Get the goal
        goal = GoalRepository.get_by_id(db, goal_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Goal with ID {goal_id} not found",
            )
        
        # Check if user owns the goal
        if goal.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this goal",
            )
        
        # Get progress entries
        progress_entries = ProgressRepository.get_by_goal_id(db, goal_id, sort_by="date", sort_desc=False)
        
        # Get latest progress
        latest_progress = ProgressRepository.get_latest_progress(db, goal_id)
        current_value = latest_progress.value if latest_progress else 0
        
        # Calculate completion percentage
        completion_percentage = GoalRepository.get_completion_percentage(db, goal_id)
        
        # Calculate time elapsed percentage
        time_elapsed_percentage = 100.0
        if goal.deadline:
            total_time = (goal.deadline - goal.start_date).total_seconds()
            elapsed_time = (datetime.now() - goal.start_date).total_seconds()
            time_elapsed_percentage = (elapsed_time / total_time) * 100 if total_time > 0 else 100
            # Cap at 100%
            time_elapsed_percentage = min(time_elapsed_percentage, 100.0)
        
        # Determine if on track
        is_on_track = completion_percentage >= time_elapsed_percentage
        
        # Generate status message
        status_message = "On Track"
        if not is_on_track:
            if completion_percentage >= time_elapsed_percentage * 0.8:
                status_message = "Slightly Behind"
            else:
                status_message = "Significantly Behind"
        elif completion_percentage >= time_elapsed_percentage * 1.2:
            status_message = "Ahead of Schedule"
        
        # Generate feedback message
        feedback = ProgressAssessmentService._generate_feedback(
            goal, 
            completion_percentage, 
            time_elapsed_percentage, 
            progress_entries
        )
        
        # Check for alerts
        alerts = ProgressAssessmentService._generate_alerts(
            goal, 
            completion_percentage, 
            time_elapsed_percentage, 
            progress_entries
        )
        
        return {
            "goal_id": goal_id,
            "completion_percentage": round(completion_percentage, 2),
            "current_value": current_value,
            "target_value": goal.target_value,
            "time_elapsed_percentage": round(time_elapsed_percentage, 2),
            "is_on_track": is_on_track,
            "status_message": status_message,
            "feedback": feedback,
            "alerts": alerts
        }
    
    @staticmethod
    def predict_completion(db: Session, goal_id: int, user_id: int) -> Dict[str, Any]:
        """Predict when the goal will be completed based on current progress."""
        # Get the goal
        goal = GoalRepository.get_by_id(db, goal_id)
        if not goal:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Goal with ID {goal_id} not found",
            )
        
        # Check if user owns the goal
        if goal.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to access this goal",
            )
        
        # Get progress entries
        progress_entries = ProgressRepository.get_by_goal_id(db, goal_id, sort_by="date", sort_desc=False)
        
        # Need at least 2 entries for prediction
        if len(progress_entries) < 2:
            return {
                "goal_id": goal_id,
                "predicted_completion_date": None,
                "predicted_final_value": None,
                "will_meet_deadline": None,
                "days_ahead_behind": None,
                "trend": "Insufficient data for prediction"
            }
        
        # Extract dates and values for prediction
        dates = [(entry.date - goal.start_date).days for entry in progress_entries]
        values = [entry.value for entry in progress_entries]
        
        # Perform linear regression to predict trend
        slope, intercept, r_value, p_value, std_err = stats.linregress(dates, values)
        
        # Calculate trend message
        if slope > 0:
            if r_value > 0.7:
                trend = "Strong positive growth"
            else:
                trend = "Moderate positive growth"
        elif slope < 0:
            if r_value < -0.7:
                trend = "Strong negative growth"
            else:
                trend = "Moderate negative growth"
        else:
            trend = "No significant change"
        
        # Only predict if we have a target value and positive slope
        predicted_completion_date = None
        predicted_final_value = None
        will_meet_deadline = None
        days_ahead_behind = None
        
        if goal.target_value and slope > 0:
            # Days needed to reach target
            days_needed = (goal.target_value - intercept) / slope if slope != 0 else float('inf')
            predicted_completion_date = goal.start_date + timedelta(days=days_needed)
            
            # Check if we'll meet the deadline
            if goal.deadline:
                will_meet_deadline = predicted_completion_date <= goal.deadline
                days_ahead_behind = (goal.deadline - predicted_completion_date).days
        
        # If we have a deadline but no target, predict the final value
        elif goal.deadline and not goal.target_value:
            days_until_deadline = (goal.deadline - goal.start_date).days
            predicted_final_value = intercept + (slope * days_until_deadline)
        
        return {
            "goal_id": goal_id,
            "predicted_completion_date": predicted_completion_date,
            "predicted_final_value": round(predicted_final_value, 2) if predicted_final_value is not None else None,
            "will_meet_deadline": will_meet_deadline,
            "days_ahead_behind": days_ahead_behind,
            "trend": trend
        }
    
    @staticmethod
    def _generate_feedback(
        goal: Goal, 
        completion_percentage: float, 
        time_elapsed_percentage: float,
        progress_entries: List
    ) -> str:
        """Generate appropriate feedback message based on progress status."""
        # Calculate ratio of progress to time elapsed
        ratio = completion_percentage / time_elapsed_percentage if time_elapsed_percentage > 0 else 1
        
        if len(progress_entries) == 0:
            return "No progress has been recorded yet. Add your first progress update to get started!"
        
        # Check progress trend
        if len(progress_entries) >= 3:
            recent_values = [entry.value for entry in progress_entries[-3:]]
            is_improving = recent_values[2] > recent_values[1] > recent_values[0]
            is_declining = recent_values[2] < recent_values[1] < recent_values[0]
        else:
            is_improving = False
            is_declining = False
        
        # Generate appropriate feedback based on status
        if ratio >= 1.2:
            if is_improving:
                return "Excellent progress! You're well ahead of schedule and your recent updates show continued improvement. Keep up the great work!"
            else:
                return "You're ahead of schedule! Your progress is exceeding expectations. Maintain this pace to achieve your goal early."
        elif ratio >= 0.9:
            if is_improving:
                return "You're on track to meet your goal. Your recent progress shows improvement, which is a great sign. Keep it up!"
            elif is_declining:
                return "You're currently on pace, but your recent progress is slowing down. Try to maintain your initial momentum to ensure you meet your goal."
            else:
                return "You're making steady progress toward your goal. Keep up the consistent effort to stay on track."
        elif ratio >= 0.7:
            if is_improving:
                return "You're slightly behind schedule, but your recent progress is trending in the right direction. With continued effort, you can get back on track."
            else:
                return "You're falling a bit behind schedule. Consider increasing your efforts to ensure you meet your deadline."
        else:
            if is_improving:
                return "You're significantly behind schedule, but your recent progress shows improvement. Keep this momentum to work toward your goal."
            else:
                return "You're considerably behind schedule. You may need to reassess your approach or adjust your goal to make it more achievable."
    
    @staticmethod
    def _generate_alerts(
        goal: Goal, 
        completion_percentage: float, 
        time_elapsed_percentage: float,
        progress_entries: List
    ) -> List[str]:
        """Generate alert messages based on progress status."""
        alerts = []
        
        # Check for no progress recorded
        if len(progress_entries) == 0:
            alerts.append("No progress recorded yet")
            return alerts
        
        # Check for inactivity
        latest_progress = progress_entries[-1]
        days_since_update = (datetime.now() - latest_progress.date).days
        
        if days_since_update > 7:
            alerts.append(f"No updates in {days_since_update} days")
        
        # Check if deadline is approaching
        if goal.deadline:
            days_to_deadline = (goal.deadline - datetime.now()).days
            if days_to_deadline <= 3 and days_to_deadline >= 0:
                alerts.append(f"Deadline approaching in {days_to_deadline} days")
            elif days_to_deadline < 0:
                alerts.append("Goal deadline has passed")
        
        # Check if significantly behind schedule
        ratio = completion_percentage / time_elapsed_percentage if time_elapsed_percentage > 0 else 1
        if ratio < 0.7 and time_elapsed_percentage > 30:
            alerts.append("Significantly behind schedule")
        
        # Check for potential goal completion soon
        if 90 <= completion_percentage < 100:
            alerts.append("Almost at goal completion")
        
        return alerts