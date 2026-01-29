"""
Procrastination Risk Prediction Module
Supports both student behavior and individual tasks
"""
import joblib
import pandas as pd
import numpy as np
import re
import os



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
        from database_setup import get_session, StudentBehavior, Student

        session = get_session()

        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            session.close()
            raise ValueError(f"Student {student_id} not found")

        if student.model_opt_out:
            session.close()
            return {
                "prediction": "disabled",
                "reason": "User opted out of predictive modeling",
                "risk_category": None,
                "risk_score": None
            }
    
        behavior = session.query(StudentBehavior).filter(
            StudentBehavior.id_student == student_id
        ).first()
        
        if not behavior:
            session.close()
            raise ValueError(f"Student {student_id} not found in database")

        features = {
            'last_minute_ratio': behavior.last_minute_ratio,
            'engagement_intensity': behavior.engagement_intensity,
            'deadline_pressure': behavior.deadline_pressure,
            'login_consistency': behavior.login_consistency,
            'early_starter': behavior.early_starter,
            'completion_rate': behavior.completion_rate,
            'activity_span': behavior.activity_span
        }

        session.close()
        return self.predict_risk(features)

    # -----------------------------
    # NEW: Task-based prediction
    # -----------------------------
    def predict_from_task(self, task_description: str, user_features=None):
        """
        Predict procrastination risk for a single task

        Parameters:
        -----------
        task_description : str
            The description of the task
        user_features : dict (optional)
            Past student behavior features

        Returns:
        --------
        dict with prediction results (same format as predict_risk)
        """

        # --- Feature extraction ---
        features_dict = {}

        # 1️⃣ Length of task
        features_dict['task_length'] = len(task_description.split())

        # 2️⃣ Keyword complexity (count of 'hard' words)
        keywords = ['essay', 'report', 'project', 'analysis', 'presentation', 'coding', 'design', 'study']
        features_dict['complexity_words'] = sum(1 for word in keywords if re.search(r'\b' + word + r'\b', task_description.lower()))

        # 3️⃣ Estimated duration (simple heuristic: words / 100)
        features_dict['estimated_duration'] = features_dict['task_length'] / 100.0  # e.g., 1 unit ~ 100 words

        # 4️⃣ Merge past user behavior if provided
        if user_features:
            features_dict.update(user_features)

        # Fill missing model features with zeros
        for feat in self.feature_names:
            if feat not in features_dict:
                features_dict[feat] = 0.0

        return self.predict_risk(features_dict)

# -----------------------------
# Example usage
# -----------------------------
if __name__ == "__main__":
    predictor = ProcrastinationPredictor()

    # Example: task-based prediction
    task_desc = "Write a 2000-word essay on climate change analysis and submit by Friday"
    task_result = predictor.predict_from_task(task_desc)
    print("\n📊 Task Prediction Result:")
    print(f"  Risk Category: {task_result['risk_category'].upper()}")
    print(f"  Risk Score: {task_result['risk_score']}/100")
    print(f"  Probability: {task_result['probability_high_risk']*100:.1f}% high-risk")

    # Example 1: Predict from feature dictionary
    example_features = {
        'last_minute_ratio': 0.6,
        'engagement_intensity': 15.5,
        'deadline_pressure': 2.5,
        'login_consistency': 1.2,
        'early_starter': 0,
        'completion_rate': 0.4,
        'activity_span': 45.0
    }
    
    result = predictor.predict_risk(example_features)
    print("\n📊 Prediction Result:")
    print(f"  Risk Category: {result['risk_category'].upper()}")
    print(f"  Risk Score: {result['risk_score']}/100")
    print(f"  Probability: {result['probability_high_risk']*100:.1f}% high-risk")
    
    # Example 2: Predict from database
    try:
        db_result = predictor.predict_from_database(student_id=11391)
        print("\n📊 Database Prediction:")
        print(f"  Risk Category: {db_result['risk_category'].upper()}")
        print(f"  Risk Score: {db_result['risk_score']}/100")
    except Exception as e:
        print(f"  Error: {e}")