"""
Procrastination Risk Prediction Module
"""
import joblib
import pandas as pd
import numpy as np

class ProcrastinationPredictor:
    """Class to handle procrastination risk predictions"""
    
    def __init__(self, model_path='models/rf_procrastination_model.pkl',
                 scaler_path='scaler.pkl',
                 features_path='models/feature_names.pkl'):
        """Load trained model and preprocessors"""
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        self.feature_names = joblib.load(features_path)
        print("✅ Model loaded successfully")
    
    def predict_risk(self, features_dict):
        """
        Predict procrastination risk for a student
        
        Parameters:
        -----------
        features_dict : dict
            Dictionary with feature names as keys:
            {
                'last_minute_ratio': float,
                'engagement_intensity': float,
                'deadline_pressure': float,
                'login_consistency': float,
                'early_starter': int (0 or 1),
                'completion_rate': float,
                'activity_span': float
            }
        
        Returns:
        --------
        dict with prediction results
        """
        # Convert to DataFrame
        features_df = pd.DataFrame([features_dict])
        
        # Ensure correct feature order
        features_df = features_df[self.feature_names]
        
        # Make prediction
        prediction = self.model.predict(features_df)[0]
        probability = self.model.predict_proba(features_df)[0]
        
        # Calculate risk score (0-100)
        risk_score = probability[1] * 100
        
        # Determine risk category
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
        """
        Predict risk for a student from database
        
        Parameters:
        -----------
        student_id : int
            Student ID from database
        
        Returns:
        --------
        dict with prediction results
        """
        from database_setup import get_session, StudentBehavior
        
        session = get_session()
        
        # Get student behavior
        behavior = session.query(StudentBehavior).filter(
            StudentBehavior.id_student == student_id
        ).first()
        
        if not behavior:
            session.close()
            raise ValueError(f"Student {student_id} not found in database")
        
        # Extract features
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

# Example usage
if __name__ == "__main__":
    # Initialize predictor
    predictor = ProcrastinationPredictor()
    
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