import pandas as pd
import numpy as np
import glob
import joblib
import os
import json
from datetime import datetime
from sqlalchemy import create_engine
from sklearn.ensemble import RandomForestClassifier
from backend.src.feedback_loop import MLFeedbackLoop
from backend.src.logger import logger

def run_training():
    # 1. Setup paths relative to project root
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    processed_dir = os.path.join(base_dir, 'data', 'processed')
    model_dir = os.path.join(base_dir, 'backend', 'src', 'models')
    os.makedirs(model_dir, exist_ok=True)

    # 2. Run the feedback loop to generate fresh data
    try:
        loop = MLFeedbackLoop(output_dir=processed_dir)
        loop.export_retraining_data()
    except Exception as e:
        logger.error(f"Feedback export failed: {e}. Proceeding with existing data.")

    # 3. Load and Merge Data
    hist_path = os.path.join(processed_dir, 'cleaned_data.csv')
    df_hist = pd.read_csv(hist_path)
    df_hist['sample_weight'] = 1.0 

    feedback_files = glob.glob(os.path.join(processed_dir, 'feedback_training_data_*.csv'))
    if feedback_files:
        df_feedback = pd.concat([pd.read_csv(f) for f in feedback_files])
        # Map feedback ground truth to the target variable
        df_feedback['high_risk'] = df_feedback['was_successful']
        df_feedback['sample_weight'] = 3.0 
        df = pd.concat([df_hist, df_feedback], ignore_index=True)
        logger.info(f"Training on merged dataset: {len(df)} total records.")
    else:
        df = df_hist
        logger.info("Training on historical data only.")

    # 4. Feature Selection & Data Cleaning
    feature_columns = [
        'last_minute_ratio', 'engagement_intensity', 'deadline_pressure', 
        'login_consistency', 'early_starter', 'completion_rate', 'activity_span'
    ]
    
    X = df[feature_columns].copy()
    y = df['high_risk'].copy()

    # Mandatory cleaning to prevent model crashes
    X = X.replace([np.inf, -np.inf], np.nan).fillna(0) 

    # 5. Weighted Training
    rf_model = RandomForestClassifier(
        n_estimators=100, 
        class_weight='balanced', 
        random_state=42,
        n_jobs=-1
    )
    
    rf_model.fit(X, y, sample_weight=df['sample_weight'])

    # 6. Save Model and Metadata
    model_path = os.path.join(model_dir, 'rf_procrastination_model.pkl')
    joblib.dump(rf_model, model_path)
    
    metadata = {
        'trained_at': datetime.now().isoformat(),
        'total_samples': len(df),
        'feedback_samples_included': len(df) - len(df_hist),
        'features': feature_columns
    }
    with open(os.path.join(model_dir, 'model_metadata.json'), 'w') as f:
        json.dump(metadata, f, indent=4)

    logger.info(f"✅ Model successfully retrained and saved to {model_path}")

def fetch_feedback_data(db_uri):
    engine = create_engine(db_uri)
    # Only pull records where we have an actual outcome to learn from
    query = """
        SELECT feature_1, feature_2, feature_3, actual_outcome 
        FROM predictions 
        WHERE actual_outcome IS NOT NULL
    """
    feedback_df = pd.read_sql(query, engine)
    return feedback_df

def train_evolving_model():
    # 1. Load static baseline data
    base_data = pd.read_csv('data/baseline_train.csv')
    
    # 2. Fetch evolving data from Phase 4 Integration
    try:
        feedback_data = fetch_feedback_data("postgresql://user:pass@localhost/db")
        # Rename columns to match baseline if necessary
        feedback_data.columns = base_data.columns 
        
        # 3. Combine datasets
        final_train_set = pd.concat([base_data, feedback_data], ignore_index=True)
        print(f"Retraining with {len(feedback_data)} new feedback samples.")
    except Exception as e:
        print(f"Feedback fetch failed, falling back to baseline: {e}")
        final_train_set = base_data

    # 4. Standard Training Logic
    X = final_train_set.drop('target', axis=1)
    y = final_train_set['target']
    
    model = RandomForestClassifier()
    model.fit(X, y)
    
    # 5. Save updated model
    # pickle.dump(model, open('model_v2.pkl', 'wb'))

if __name__ == "__main__":
    run_training()