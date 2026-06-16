import pandas as pd
from datetime import timedelta
from sqlalchemy import create_engine
from backend.app.database import DATABASE_URL
from backend.app.models import Interaction, Nudge, Prediction
from sqlalchemy.orm import sessionmaker

# Set up Database Connection
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def calculate_research_metrics():
    session = SessionLocal()
    
    # 1. Load Data into DataFrames
    nudges = pd.read_sql(session.query(Nudge).statement, engine)
    interactions = pd.read_sql(session.query(Interaction).statement, engine)
    predictions = pd.read_sql(session.query(Prediction).statement, engine)
    
    if nudges.empty or predictions.empty:
        print("Insufficient data to calculate metrics.")
        return

    print("--- RemindAI Phase 4: Research Metrics ---")

    # --- METRIC 1: Nudge Compliance Rate ---
    # Definition: Interaction (action) occurring within 4 hours after a nudge
    compliance_events = []
    for _, nudge in nudges.iterrows():
        # Look for interactions by the same student shortly after the nudge
        relevant_actions = interactions[
            (interactions['student_id'] == nudge['student_id']) &
            (interactions['timestamp'] > nudge['sent_at']) &
            (interactions['timestamp'] <= nudge['sent_at'] + timedelta(hours=4))
        ]
        if not relevant_actions.empty:
            compliance_events.append(nudge['id'])

    compliance_rate = (len(compliance_events) / len(nudges)) * 100
    print(f"Nudge Compliance Rate: {compliance_rate:.2f}%")
    print(f"Total Nudges Sent: {len(nudges)} | Compliant Actions: {len(compliance_events)}")

    # --- METRIC 2: Average Reduction in P_fail ---
    # Definition: Risk score before nudge vs. Risk score ~24h after
    reductions = []
    
    for _, nudge in nudges.iterrows():
        # Get prediction immediately before nudge
        pred_before = predictions[
            (predictions['student_id'] == nudge['student_id']) &
            (predictions['predicted_at'] <= nudge['sent_at'])
        ].sort_values(by='predicted_at', ascending=False)

        # Get prediction roughly 24 hours later
        pred_after = predictions[
            (predictions['student_id'] == nudge['student_id']) &
            (predictions['predicted_at'] > nudge['sent_at'] + timedelta(hours=20)) &
            (predictions['predicted_at'] <= nudge['sent_at'] + timedelta(hours=28))
        ].sort_values(by='predicted_at', ascending=True)

        if not pred_before.empty and not pred_after.empty:
            risk_before = pred_before['risk_score'].iloc[0]
            risk_after = pred_after['risk_score'].iloc[0]
            reductions.append(risk_before - risk_after)

    if reductions:
        avg_reduction = sum(reductions) / len(reductions)
        print(f"Average Reduction in P_fail (Post-Nudge): {avg_reduction:.4f}")
        print(f"Based on {len(reductions)} measured nudge cycles.")
    else:
        print("Not enough 24-hour follow-up prediction data yet.")

    session.close()

if __name__ == "__main__":
    calculate_research_metrics()