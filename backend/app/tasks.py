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

@celery_app.task(name="sync_school_data", bind=True, max_retries=2, default_retry_delay=60)
def sync_school_data_task(self, student_id: int):
    """
    Background worker task to fetch and deduplicate external assignments.
    """
    try:
        with get_db_session() as session:
            from backend.src.logger import sync_logger
            from backend.src.ingestion import AssignmentIngestor
            from backend.app.models import Notification
            import datetime
            
            sync_logger.info(f"Worker syncing external assignments for student ID: {student_id}")
            ingestor = AssignmentIngestor(session)
            res = ingestor.sync_for_student(student_id)
            
            if not res.get("success"):
                if res.get("needs_reauth"):
                    sync_logger.warning(f"SYNC_AUTH_EXPIRED: Student {student_id} external auth token expired.")
                    
                    # Generate an in-app notification so rotation is exposed directly in the UI
                    notif = Notification(
                        student_id=student_id,
                        type="system",
                        title="Connection Expired",
                        message="Your external school account token expired. Please safely sign out and log back in with Google to restore syncing.",
                        created_at=datetime.datetime.utcnow(),
                        status="unread"
                    )
                    session.add(notif)
                    session.commit()
                else:
                    sync_logger.error(f"SYNC_FAILED: Student {student_id} external sync failed: {res.get('error')}")
            else:
                sync_logger.info(f"SYNC_SUCCESS: Synced {res.get('synced_count', 0)} tasks for student {student_id}")
            
            return f"Completed sync for student {student_id}"
            
    except Exception as exc:
        from backend.src.logger import sync_logger
        sync_logger.error(f"Worker failure syncing student {student_id}: {exc}")
        raise self.retry(exc=exc)