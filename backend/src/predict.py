"""
Procrastination Risk Prediction Module
Supports both student behavior and individual tasks
"""
import joblib
import pandas as pd
import numpy as np
import re
import os
from datetime import datetime, timezone
from backend.app.database import get_db_session
from backend.app.models import StudentBehavior, Student
from backend.app.models import Prediction, Commitment 
from .logger import logger

class ProcrastinationPredictor:
    """Class to handle procrastination risk predictions"""

    def __init__(self, model_path = os.path.join(os.path.dirname(__file__), "models/rf_procrastination_model.pkl"),
                 scaler_path=os.path.join(os.path.dirname(__file__), "models/scaler.pkl"),
                 features_path=os.path.join(os.path.dirname(__file__), "models/feature_names.pkl")):
        """Load trained model and preprocessors"""
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_names = joblib.load(features_path)
        print("Model loaded successfully")

    # -----------------------------
    # Existing method: student features
    # -----------------------------
    def predict_risk(self, features_dict):
        features_df = pd.DataFrame([features_dict])

        # Ensure all expected features exist, filling missing with 0.0
        for col in self.feature_names:
            if col not in features_df.columns:
                features_df[col] = 0.0

        features_df = features_df[self.feature_names]
        prediction = self.model.predict(features_df)[0]
        probability = self.model.predict_proba(features_df)[0]
        risk_score = probability[1] * 100

        if risk_score < 33:
            risk_category = 'low'
        elif risk_score < 67:
            risk_category = 'medium'
        else:
            risk_category = 'high'

        return {
            'prediction': 'high_risk' if prediction == 1 else 'low_risk',
            'risk_score': round(risk_score, 2),
            'risk_category': risk_category,
            'probability_high_risk': round(probability[1], 3),
            'probability_low_risk': round(probability[0], 3)
        }

    def predict_from_database(self, student_id):
        with get_db_session() as session:  # Auto-closes session
            student = session.query(Student).filter_by(id=student_id).first()
            if not student:
                return (f"Student {student_id} not found")

            if student.model_opt_out:
                return {
                    "prediction": "disabled",
                    "reason": "User opted out of predictive modeling",
                    "risk_category": None,
                    "risk_score": 50
                }
        
            behavior = session.query(StudentBehavior).filter(
                StudentBehavior.student_id == student_id
            ).first()
            
            if not behavior:
                logger.info(f"New student {student_id} detected. Using default risk profile.")
                # Return a default risk score (e.g., 50%) or a mock data structure
                return {
                    'p_fail': 0.5, 
                    'risk_category': 'Medium',
                    'is_new_user': True
                }

            now = datetime.utcnow()

            features = {
                'last_minute_ratio': behavior.last_minute_ratio,
                'engagement_intensity': behavior.engagement_intensity,
                'deadline_pressure': behavior.deadline_pressure,
                'login_consistency': behavior.login_consistency,
                'early_starter': behavior.early_starter,
                'completion_rate': behavior.completion_rate,
                'activity_span': behavior.activity_span,
                'hour_of_day': now.hour,
                'day_of_week': now.weekday()  # 0=Monday, 6=Sunday
            }

            return self.predict_risk(features)

    def update_all_commitment_risks(self):
        with get_db_session() as session:
            # 1. Get all commitments that are still pending
            commitments = session.query(Commitment).filter_by(status='pending').all()
            
            for c in commitments:
                # 2. Predict risk using the task title/custom title
                task_text = c.custom_title or (c.assignment.title if c.assignment else "Task")
                prediction_result = self.predict_from_task(task_text)
                
                # 3. Save to the predictions table
                new_pred = Prediction(
                    student_id=c.student_id,
                    assignment_id=c.assignment_id, # Can be None for custom tasks
                    risk_score=prediction_result['probability_high_risk'],
                    predicted_at=datetime.utcnow()
                )
                session.add(new_pred)
                print(f" Saved {prediction_result['risk_score']}% risk for: {task_text}")
                
            session.commit()
    # -----------------------------
    # NEW: Task-based prediction
    # -----------------------------
    def predict_from_task(self, task_description: str, student_id:int=None):
        now = datetime.utcnow()

        task_length = len(task_description.split())
    
        # Heuristic: Count "high-effort" keywords
        heavy_keywords = ['thesis', 'exam', 'final', 'project', 'research', 'essay', 'complete']
        complexity = sum(2 for word in heavy_keywords if word in task_description.lower())
        
        features_dict = {
            'task_length': task_length,
            'hour_of_day': now.hour,
            'day_of_week': now.weekday(),
            'complexity_words': complexity,
            'estimated_duration': task_length / 5.0, 
        }

        # IMPORTANT: Fetch real student history if available
        if student_id:
            with get_db_session() as session:
                behavior = session.query(StudentBehavior).filter_by(student_id=student_id).first()
                if behavior:
                    features_dict.update({
                        'last_minute_ratio': behavior.last_minute_ratio or 0.5,
                'completion_rate': behavior.completion_rate or 0.5,
                'engagement_intensity': behavior.engagement_intensity or 10.0,
                # 'deadline_pressure': behavior.deadline_pressure or 0.0,
                # 'login_consistency': behavior.login_consistency or 0.0,
                # 'early_starter': behavior.early_starter or 0,
                # 'activity_span': behavior.activity_span or 0.0
                    })
                else:
                    # Fallback for new students with no history
                    is_long_task = 1 if task_length > 10 else 0
                    features_dict.update({
                        'last_minute_ratio': 0.2 + (is_long_task * 0.4), # Higher risk for longer tasks
                        'completion_rate': 0.8 - (is_long_task * 0.3),
                        'engagement_intensity': 5.0 + (is_long_task * 10)
                        # 'deadline_pressure': 1.0,
                        # 'login_consistency': 0.8,
                        # 'early_starter': 1,
                        # 'activity_span': 10.0
                    })
                
        return self.predict_risk(features_dict)

    def refresh_behavior_stats(self, student_id):
        with get_db_session() as session:
            # 1. Fetch all historical commitments
            all_commits = session.query(Commitment).filter_by(student_id=student_id).all()
            
            if not all_commits:
                return

            total = len(all_commits)
            kept = len([c for c in all_commits if c.status == 'kept'])
            in_progress = len([c for c in all_commits if c.status == 'in_progress'])
            broken = len([c for c in all_commits if c.status == 'broken'])
            
            # 2. Calculate Ratios
            effective_success = kept + (in_progress * 0.5)
            completion_rate = effective_success / total if total > 0 else 0.5            
            # Logic for 'last_minute_ratio': 
            # Tasks finished within 2 hours of deadline / total kept tasks
            last_minute_count = 0
            for c in all_commits:
                if c.status == 'kept' and c.assignment:
                    # Assuming you have a 'completed_at' timestamp
                    if c.completed_at and (c.assignment.due_date - c.completed_at).total_seconds() < 7200:
                        last_minute_count += 1
            
            last_minute_ratio = last_minute_count / kept if kept > 0 else 0.2

            # 3. Update or Create the StudentBehavior record
            behavior = session.query(StudentBehavior).filter_by(student_id=student_id).first()
            
            if not behavior:
                behavior = StudentBehavior(student_id=student_id)
                session.add(behavior)

            behavior.last_minute_ratio = last_minute_ratio

            in_progress_count = session.query(Commitment).filter_by(
                student_id=student_id, 
                status='in_progress'
            ).count()

            # If they just started a task, we SLASH the risk score manually 
            # to override the Random Forest's "Deadline Pressure" bias.
            if in_progress_count > 0:
                behavior.engagement_intensity = 1.0  
                # We give them a 'perfect' completion rate for the next prediction
                behavior.completion_rate = 1.0 
                logger.info(f"User {student_id} is active. Forcing risk reduction.")


            if in_progress > 0:
                behavior.engagement_intensity = 1.0  # Max engagement
                behavior.completion_rate = min(1.0, behavior.completion_rate + 0.3) # Artificial temporary boost
            else:
                behavior.engagement_intensity = 0.3 # Low engagement if nothing is active
            
            new_risk = self.predict_from_database(student_id) # Get new AI score

            risk_value = new_risk.get('risk_score') or new_risk.get('probability_high_risk') or 0.5
    
            from backend.app.models import Prediction
            with get_db_session() as session:
                new_pred = Prediction(
                    student_id=student_id,
                    risk_score=float(risk_value), # Ensure it's a float
                    predicted_at=datetime.now(timezone.utc)
                )
                session.add(new_pred)

                session.commit()
            logger.info(f" Updated behavior stats for Student {student_id}: Rate={completion_rate:.2f}")
            logger.info(f"Risk Discount Applied for Student {student_id}. New Engagement: {behavior.engagement_intensity}")
# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    predictor = ProcrastinationPredictor()
    
    print(" Starting risk updates for all pending commitments...")
    predictor.update_all_commitment_risks()
    print(" Finished updating database.")