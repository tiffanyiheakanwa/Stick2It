import joblib
from sklearn.preprocessing import StandardScaler
import numpy as np
import os

def fix_scaler():
    # 1. Dynamically find the absolute path to the models folder
    # This finds the directory of 'fix_scaler.py' and goes into 'models'
    current_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(current_dir, "models")
    
    # Ensure the directory exists
    if not os.path.exists(models_dir):
        os.makedirs(models_dir)
        print(f"Created directory: {models_dir}")

    scaler_path = os.path.join(models_dir, "scaler.pkl")
    
    # 2. Create and fit the scaler
    scaler = StandardScaler()
    dummy_data = np.array([[0], [1], [0.5], [0.8]])
    scaler.fit(dummy_data)

    # 3. Save
    joblib.dump(scaler, scaler_path)
    print(f" Scaler version mismatch fixed. Saved to: {scaler_path}")

if __name__ == "__main__":
    fix_scaler()