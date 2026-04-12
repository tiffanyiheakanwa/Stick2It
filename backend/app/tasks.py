from .celery_app import celery_app
from backend.src.nudge_system import SmartNudgeSystem
from backend.app.database import get_db_session
from backend.src.logger import logger
from backend.src.train_evolving_model import retrain_from_db

# Initialize the service inside the worker
nudge_service = SmartNudgeSystem()

@celery_app.task(
    name="process_student_nudge",
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def process_student_nudge_task(self, student_id: int):
    """
    Background worker task to check and send nudges for a specific student.
    """
    try:
        with get_db_session() as session:
            logger.info(f" Worker processing student ID: {student_id}")
            
            # 1. Run the AI risk assessment and send nudges
            nudge_service.check_and_send_nudges(student_id)
            
            # 2. Run the Loss Aversion (streak protection) check
            nudge_service.trigger_streak_protection_cycle(student_id)
            
            return f"Completed nudges for student {student_id}"
            
    except Exception as exc:
        logger.error(f" Worker failure for student {student_id}: {exc}")
        # Retry the task if it fails (e.g., database lock)
        raise self.retry(exc=exc)

@celery_app.task(name="evolve_ai_model")
def evolve_ai_model():
    logger.info("Starting weekly AI evolution cycle...")
    retrain_from_db()
    logger.info("AI evolution complete. New patterns integrated.")