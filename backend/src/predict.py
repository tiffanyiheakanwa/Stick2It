"""
Procrastination Risk Prediction Module
Supports both student behavior and individual tasks
"""
import joblib
import pandas as pd
import numpy as np
import re
import os
from datetime import datetime
from backend.app.database import get_db_session
from backend.app.models import StudentBehavior, Student
from backend.app.models import Prediction, Commitment 

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
                raise ValueError(f"Student {student_id} not found")

            if student.model_opt_out:
                return {
                    "prediction": "disabled",
                    "reason": "User opted out of predictive modeling",
                    "risk_category": None,
                    "risk_score": None
                }
        
            behavior = session.query(StudentBehavior).filter(
                StudentBehavior.student_id == student_id
            ).first()
            
            if not behavior:
                raise ValueError(f"New student {student_id} detected. Using default risk profile.")
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

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    predictor = ProcrastinationPredictor()
    
    print(" Starting risk updates for all pending commitments...")
    predictor.update_all_commitment_risks()
    print(" Finished updating database.")