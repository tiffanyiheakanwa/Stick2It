import pandas as pd
from backend.app.database import SessionLocal
from backend.app.models import Prediction
from sklearn.ensemble import RandomForestClassifier
import joblib

def retrain_from_db():
    db = SessionLocal()
    try:
        # 1. Fetch data where we actually have an outcome (the 'truth')
        query = db.query(Prediction).filter(Prediction.actual_outcome.isnot(None))
        data = pd.read_sql(query.statement, db.bind)

        if len(data) < 10: # Minimum threshold to justify retraining
            print(" Not enough new data to retrain yet. Keep collecting!")
            return

        # 2. Define Features (X) and Target (y)
        # Note: Ensure these column names match what your model expects
        X = data[['risk_score']] # You can expand this with behavioral features
        y = data['actual_outcome']

        # 3. Train the updated model
        model = RandomForestClassifier(n_estimators=100)
        model.fit(X, y)

        # 4. Save with current Scikit-Learn version (Fixes the version warning!)
        joblib.dump(model, 'backend/src/models/procrastination_model.pkl')
        print(" AI Evolved! Model updated with real student behavior data.")

    finally:
        db.close()

if __name__ == "__main__":
    retrain_from_db()