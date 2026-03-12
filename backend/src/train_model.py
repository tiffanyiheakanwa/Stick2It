# %%
# Cell 1: Import libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             f1_score, confusion_matrix, classification_report,
                             roc_auc_score, roc_curve)
import joblib
import warnings
warnings.filterwarnings('ignore')

print("✅ All libraries imported successfully!")

# %%
# Cell 2: Load cleaned data
df = pd.read_csv('../data/processed/cleaned_data.csv')

print(f"Dataset loaded: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nFirst few rows:")
print(df.head())

# %%
# Cell 3: Define features and target
# These are the 7 features we engineered on Day 2
feature_columns = [
    'last_minute_ratio',
    'engagement_intensity', 
    'deadline_pressure',
    'login_consistency',
    'early_starter',
    'completion_rate',
    'activity_span'
]

target_column = 'high_risk'

# Extract features and target
X = df[feature_columns].copy()
y = df[target_column].copy()

print("Feature Matrix (X):")
print(f"  Shape: {X.shape}")
print(f"  Features: {feature_columns}")
print(f"\nTarget Variable (y):")
print(f"  Shape: {y.shape}")
print(f"  Distribution:\n{y.value_counts()}")
print(f"  High-risk percentage: {y.mean()*100:.1f}%")

# %%
# Cell 4: Check for missing values and data quality
print("Data Quality Check:")
print("=" * 60)
print(f"\nMissing values in features:")
print(X.isnull().sum())
print(f"\nMissing values in target:")
print(y.isnull().sum())

# Handle any missing values (if any)
if X.isnull().sum().sum() > 0:
    print(f"\n⚠️  Found {X.isnull().sum().sum()} missing values - filling with 0")
    X = X.fillna(0)

# Check for infinite values
inf_count = np.isinf(X).sum().sum()
if inf_count > 0:
    print(f"\n⚠️  Found {inf_count} infinite values - replacing with 0")
    X = X.replace([np.inf, -np.inf], 0)

print("\n✅ Data is clean and ready for training!")

# %%
# Cell 5: Feature statistics by class
print("Feature Statistics by Risk Level:")
print("=" * 60)

for feature in feature_columns:
    print(f"\n{feature}:")
    print(f"  High Risk - Mean: {X[y==1][feature].mean():.3f}, Std: {X[y==1][feature].std():.3f}")
    print(f"  Low Risk  - Mean: {X[y==0][feature].mean():.3f}, Std: {X[y==0][feature].std():.3f}")
    print(f"  Difference: {X[y==1][feature].mean() - X[y==0][feature].mean():.3f}")

# %%
# Cell 6: Visualize feature distributions
fig, axes = plt.subplots(3, 3, figsize=(15, 12))
axes = axes.ravel()

for idx, feature in enumerate(feature_columns):
    axes[idx].hist(X[y==0][feature], bins=30, alpha=0.5, label='Low Risk', color='green')
    axes[idx].hist(X[y==1][feature], bins=30, alpha=0.5, label='High Risk', color='red')
    axes[idx].set_xlabel(feature)
    axes[idx].set_ylabel('Count')
    axes[idx].legend()
    axes[idx].set_title(f'Distribution: {feature}')

# Hide unused subplots
for idx in range(len(feature_columns), len(axes)):
    axes[idx].axis('off')

plt.tight_layout()
plt.show()

# %%
# Cell 7: Split data into training and testing sets
# 80% training, 20% testing
X_train, X_test, y_train, y_test = train_test_split(
    X, y, 
    test_size=0.2,      # 20% for testing
    random_state=42,    # For reproducibility
    stratify=y          # Maintain class balance
)

print("Train/Test Split:")
print("=" * 60)
print(f"Training set: {X_train.shape[0]} samples ({X_train.shape[0]/len(X)*100:.1f}%)")
print(f"Testing set:  {X_test.shape[0]} samples ({X_test.shape[0]/len(X)*100:.1f}%)")
print(f"\nClass distribution in training:")
print(y_train.value_counts())
print(f"High-risk: {y_train.mean()*100:.1f}%")
print(f"\nClass distribution in testing:")
print(y_test.value_counts())
print(f"High-risk: {y_test.mean()*100:.1f}%")

# %%
# Cell 8: Feature scaling (important for some models)
# Random Forest doesn't strictly need scaling, but we'll do it for completeness
scaler = StandardScaler()

# Fit on training data only (avoid data leakage)
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Convert back to DataFrame for easier handling
X_train_scaled = pd.DataFrame(X_train_scaled, columns=feature_columns)
X_test_scaled = pd.DataFrame(X_test_scaled, columns=feature_columns)

print("✅ Features scaled using StandardScaler")
print(f"\nScaled training data shape: {X_train_scaled.shape}")
print(f"\nSample scaled values:")
print(X_train_scaled.head())

# Save the scaler for later use
joblib.dump(scaler, '../src/scaler.pkl')
print("\n✅ Scaler saved to: src/scaler.pkl")

# %%
# Cell 9: Train Logistic Regression (simple baseline)
print("Training Logistic Regression (Baseline)...")
print("=" * 60)

lr_model = LogisticRegression(random_state=42, max_iter=1000)
lr_model.fit(X_train_scaled, y_train)

# Make predictions
y_pred_lr = lr_model.predict(X_test_scaled)
y_pred_proba_lr = lr_model.predict_proba(X_test_scaled)[:, 1]

# Calculate metrics
lr_accuracy = accuracy_score(y_test, y_pred_lr)
lr_precision = precision_score(y_test, y_pred_lr)
lr_recall = recall_score(y_test, y_pred_lr)
lr_f1 = f1_score(y_test, y_pred_lr)
lr_auc = roc_auc_score(y_test, y_pred_proba_lr)

print("\n📊 Logistic Regression Results:")
print(f"  Accuracy:  {lr_accuracy:.3f}")
print(f"  Precision: {lr_precision:.3f}")
print(f"  Recall:    {lr_recall:.3f}")
print(f"  F1-Score:  {lr_f1:.3f}")
print(f"  ROC-AUC:   {lr_auc:.3f}")

print("\n✅ Baseline model trained!")

# %%
# Cell 10: Train Random Forest Classifier
print("Training Random Forest Classifier...")
print("=" * 60)

# Initialize Random Forest with good default parameters
rf_model = RandomForestClassifier(
    n_estimators=100,        # Number of trees
    max_depth=10,            # Max depth of each tree
    min_samples_split=20,    # Min samples to split a node
    min_samples_leaf=10,     # Min samples in leaf node
    random_state=42,
    n_jobs=-1,               # Use all CPU cores
    verbose=1                # Show progress
)

# Train the model
rf_model.fit(X_train, y_train)  # Random Forest works well with unscaled data

print("\n✅ Random Forest trained!")

# %%
# Cell 11: Make predictions with Random Forest
y_pred_rf = rf_model.predict(X_test)
y_pred_proba_rf = rf_model.predict_proba(X_test)[:, 1]

# Calculate metrics
rf_accuracy = accuracy_score(y_test, y_pred_rf)
rf_precision = precision_score(y_test, y_pred_rf)
rf_recall = recall_score(y_test, y_pred_rf)
rf_f1 = f1_score(y_test, y_pred_rf)
rf_auc = roc_auc_score(y_test, y_pred_proba_rf)

print("📊 Random Forest Results:")
print("=" * 60)
print(f"  Accuracy:  {rf_accuracy:.3f} ({rf_accuracy*100:.1f}%)")
print(f"  Precision: {rf_precision:.3f}")
print(f"  Recall:    {rf_recall:.3f}")
print(f"  F1-Score:  {rf_f1:.3f}")
print(f"  ROC-AUC:   {rf_auc:.3f}")

# %%
# Cell 12: Compare models side-by-side
comparison_df = pd.DataFrame({
    'Model': ['Logistic Regression', 'Random Forest'],
    'Accuracy': [lr_accuracy, rf_accuracy],
    'Precision': [lr_precision, rf_precision],
    'Recall': [lr_recall, rf_recall],
    'F1-Score': [lr_f1, rf_f1],
    'ROC-AUC': [lr_auc, rf_auc]
})

print("\n📊 MODEL COMPARISON:")
print("=" * 60)
print(comparison_df.to_string(index=False))

# Determine best model
best_model_name = 'Random Forest' if rf_f1 > lr_f1 else 'Logistic Regression'
best_model = rf_model if rf_f1 > lr_f1 else lr_model
print(f"\n🏆 Best Model: {best_model_name}")

# %%
# Cell 13: Confusion Matrix
from sklearn.metrics import ConfusionMatrixDisplay

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Logistic Regression
cm_lr = confusion_matrix(y_test, y_pred_lr)
disp_lr = ConfusionMatrixDisplay(confusion_matrix=cm_lr, 
                                  display_labels=['Low Risk', 'High Risk'])
disp_lr.plot(ax=axes[0], cmap='Blues')
axes[0].set_title(f'Logistic Regression\nAccuracy: {lr_accuracy:.3f}')

# Random Forest
cm_rf = confusion_matrix(y_test, y_pred_rf)
disp_rf = ConfusionMatrixDisplay(confusion_matrix=cm_rf,
                                  display_labels=['Low Risk', 'High Risk'])
disp_rf.plot(ax=axes[1], cmap='Greens')
axes[1].set_title(f'Random Forest\nAccuracy: {rf_accuracy:.3f}')

plt.tight_layout()
plt.show()

# Interpret confusion matrix for Random Forest
print("\n📊 Random Forest Confusion Matrix Interpretation:")
print("=" * 60)
print(f"True Negatives (correctly predicted low-risk):  {cm_rf[0,0]}")
print(f"False Positives (low-risk predicted as high):   {cm_rf[0,1]}")
print(f"False Negatives (high-risk predicted as low):   {cm_rf[1,0]}")
print(f"True Positives (correctly predicted high-risk): {cm_rf[1,1]}")

# %%
# Cell 14: ROC Curve
plt.figure(figsize=(10, 6))

# Logistic Regression ROC
fpr_lr, tpr_lr, _ = roc_curve(y_test, y_pred_proba_lr)
plt.plot(fpr_lr, tpr_lr, label=f'Logistic Regression (AUC = {lr_auc:.3f})', 
         linewidth=2, color='blue')

# Random Forest ROC
fpr_rf, tpr_rf, _ = roc_curve(y_test, y_pred_proba_rf)
plt.plot(fpr_rf, tpr_rf, label=f'Random Forest (AUC = {rf_auc:.3f})', 
         linewidth=2, color='green')

# Diagonal reference line
plt.plot([0, 1], [0, 1], 'k--', label='Random Classifier')

plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curves - Model Comparison')
plt.legend()
plt.grid(alpha=0.3)
plt.show()

# %%
# Cell 15: Feature Importance (Random Forest only)
feature_importance = pd.DataFrame({
    'feature': feature_columns,
    'importance': rf_model.feature_importances_
}).sort_values('importance', ascending=False)

print("\n🔍 FEATURE IMPORTANCE:")
print("=" * 60)
print(feature_importance.to_string(index=False))

# Visualize
plt.figure(figsize=(10, 6))
plt.barh(feature_importance['feature'], feature_importance['importance'])
plt.xlabel('Importance Score')
plt.title('Feature Importance - Random Forest')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.show()

# %%
# Cell 16: Detailed classification report
print("\n📋 DETAILED CLASSIFICATION REPORT:")
print("=" * 60)
print("\nRandom Forest:")
print(classification_report(y_test, y_pred_rf, 
                           target_names=['Low Risk', 'High Risk']))

# %%
# Cell 17: Save the best model
import os

# Create models directory
os.makedirs('../src/models', exist_ok=True)

# Save Random Forest model
model_path = '../src/models/rf_procrastination_model.pkl'
joblib.dump(rf_model, model_path)
print(f"✅ Model saved to: {model_path}")

# Save feature names (important for production)
feature_names_path = '../src/models/feature_names.pkl'
joblib.dump(feature_columns, feature_names_path)
print(f"✅ Feature names saved to: {feature_names_path}")

# Save model metadata
metadata = {
    'model_type': 'RandomForestClassifier',
    'accuracy': rf_accuracy,
    'precision': rf_precision,
    'recall': rf_recall,
    'f1_score': rf_f1,
    'roc_auc': rf_auc,
    'n_estimators': 100,
    'training_samples': len(X_train),
    'test_samples': len(X_test),
    'feature_names': feature_columns,
    'trained_date': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
}

import json
metadata_path = '../src/models/model_metadata.json'
with open(metadata_path, 'w') as f:
    json.dump(metadata, f, indent=4)
print(f"✅ Metadata saved to: {metadata_path}")

# %%
# Cell 18: Test loading the saved model
print("\n🧪 Testing model loading...")
loaded_model = joblib.load(model_path)
loaded_features = joblib.load(feature_names_path)

# Make a test prediction
test_sample = X_test.iloc[0:1]
prediction = loaded_model.predict(test_sample)
probability = loaded_model.predict_proba(test_sample)[0]

print(f"\n✅ Model loaded successfully!")
print(f"\nTest prediction:")
print(f"  Features: {test_sample.values[0]}")
print(f"  Prediction: {'High Risk' if prediction[0] == 1 else 'Low Risk'}")
print(f"  Probability: {probability[1]*100:.1f}% high-risk")

# %%



