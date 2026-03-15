import os
import pandas as pd
from datetime import datetime
from sqlalchemy import and_
from backend.src.logger import logger
from backend.app.database import get_db_session
from backend.app.models import (
    Nudge, 
    Prediction, 
    Commitment, 
    StudentBehavior, 
    Student
)

class MLFeedbackLoop:
    def __init__(self, output_dir="data/processed"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def export_retraining_data(self):
        """
        Aggregates nudge interventions, AI risk scores, and actual outcomes 
        to create a feedback dataset for model retraining.
        """
        logger.info("🔄 Starting ML Feedback Loop: Aggregating intervention outcomes...")
        
        with get_db_session() as session:
            # Join Nudges, Predictions, and Commitments to correlate AI advice with behavior
            # and ground truth (Commitment status)
            query = session.query(
                Nudge.student_id,
                Nudge.nudge_type,
                Nudge.sent_at.label("intervention_time"),
                Prediction.risk_score.label("ai_predicted_risk"),
                Commitment.status.label("outcome"),
                Commitment.stake_value,
                StudentBehavior.last_minute_ratio,
                StudentBehavior.engagement_intensity
            ).join(
                # Link nudge to the specific prediction that triggered it
                Prediction, and_(
                    Nudge.student_id == Prediction.student_id,
                    Nudge.assignment_id == Prediction.assignment_id
                )
            ).join(
                # Link to the commitment to see if it was 'kept' or 'broken'
                Commitment, and_(
                    Nudge.student_id == Commitment.student_id,
                    Nudge.assignment_id == Commitment.assignment_id
                )
            ).join(
                # Pull behavioral features to understand 'who' responded to 'what'
                StudentBehavior, Nudge.student_id == StudentBehavior.student_id
            ).filter(
                Commitment.status.in_(['kept', 'broken']) # Only export finalized outcomes
            )

            results = query.all()

            if not results:
                logger.warning("⚠️ No finalized intervention outcomes found for export.")
                return None

            # Convert to DataFrame for ML processing
            df = pd.DataFrame([r._asdict() for r in results])
            
            # Label encoding for the outcome (Ground Truth for retraining)
            df['was_successful'] = df['outcome'].apply(lambda x: 1 if x == 'kept' else 0)

            # Save to the processed data directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"feedback_training_data_{timestamp}.csv"
            filepath = os.path.join(self.output_dir, filename)
            
            df.to_csv(filepath, index=False)
            logger.info(f"✅ Feedback data exported to {filepath} ({len(df)} records).")
            return filepath

    def analyze_nudge_effectiveness(self):
        """
        Optional: Logs which nudge types are currently performing best.
        """
        with get_db_session() as session:
            # Simple aggregation of success rates by nudge category
            with get_db_session() as session:
                data = session.query(Nudge.nudge_type, Commitment.status).join(
                    Commitment, Nudge.assignment_id == Commitment.assignment_id
                ).all()
                
                if not data:
                    return

                df = pd.DataFrame(data, columns=['type', 'status'])
                stats = df.groupby('type')['status'].value_counts(normalize=True).unstack().fill_value(0)
                logger.info(f"📊 Current Nudge Effectiveness Stats:\n{stats}")

if __name__ == "__main__":
    # This allows the script to be run as a standalone cron job or task
    loop = MLFeedbackLoop()
    loop.export_retraining_data()
    loop.analyze_nudge_effectiveness()