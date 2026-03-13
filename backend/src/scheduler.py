"""
Stick2It – Background Scheduler
Runs automated checks & nudges
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import traceback
from .commitment_system import CommitmentSystem
from .nudge_system import SmartNudgeSystem
from .progress import ProgressTracker
from .utils import safe_execute
from .logger import logger
from backend.app.models import Student



# Initialize systems
commitment_system = CommitmentSystem()
nudge_system = SmartNudgeSystem()
progress_tracker = ProgressTracker()

# Initialize scheduler
scheduler = BackgroundScheduler()

# =========================
# JOB FUNCTIONS
# =========================

def check_commitments():
    """Check commitments and handle points/streaks"""
    try:
        print("Checking commitments...")
        from backend.app.database import get_db_session
        from backend.app.models import Commitment
        
        with get_db_session() as session:
            # Fetch all pending tasks that need checking
            logger.info("Running job: check_commitments")
            pending = session.query(Commitment).filter_by(status='pending').all()
            for c in pending:
                # Pass the ID to the check function
                commitment_system.check_commitment(c.id)
            
            
    except Exception as e:
        print(f"Error in check_commitments: {e}")
        logger.error(f"Error in check_commitments: {e}")
        traceback.print_exc()

def send_nudges():
    """Run nudge engine to send personalized nudges"""
    try:
        print(f" [{datetime.utcnow()}] Running nudge engine...")
        logger.info(" Running job: send_nudges")
        safe_execute(nudge_system.check_and_send_nudges(student_id=None))
    except Exception as e:
        print(f" Error in send_nudges: {e}")
        logger.error(f" Error in send_nudges: {e}")
        traceback.print_exc()

def update_streaks():
    """Update daily streaks for all students"""
    try:
        print(f" [{datetime.utcnow()}] Updating daily streaks...")
        logger.info(" Running job: update_streaks")
        safe_execute(progress_tracker.update_daily_streaks)
    except Exception as e:
        print(f" Error in update_streaks: {e}")
        traceback.print_exc()

def protect_streaks():
    """NEW: Specific check for students at risk of losing streaks."""
    try:
        from backend.app.database import get_db_session
        with get_db_session() as session:
            logger.info(" Running job: protect_streaks")
            # Logic triggers specifically for 'Streak at Risk' nudges

            students = session.query(Student).all()

            for student in students:
                safe_execute(
                    nudge_system.trigger_streak_protection_cycle(student.id)
                )
            
    except Exception as e:
        logger.error(f" Error in protect_streaks: {e}")

# =========================
# SCHEDULE JOBS
# =========================

scheduler.add_job(check_commitments, "interval", minutes=30, id="check_commitments")
scheduler.add_job(send_nudges, "interval", minutes=60, id="send_nudges")
scheduler.add_job(protect_streaks, "cron", hour="18-23", id="streak_protection")
scheduler.add_job(update_streaks, "cron", hour=0, id="update_streaks")  # runs at midnight

# =========================
# START SCHEDULER
# =========================

def start_scheduler():
    try:
        scheduler.start()
        logger.info(" Scheduler started successfully")
        print(" Scheduler started")
        print(" Jobs scheduled:")
        for job in scheduler.get_jobs():
            print(f" - {job.id} next run at {job.next_run_time}")
    except Exception as e:
        logger.error(f" Failed to start scheduler: {e}")
        logger.error("Scheduler will retry on next launch")
        print(f" Failed to start scheduler: {e}")
        traceback.print_exc()

# =========================
# RUN DIRECTLY
# =========================

if __name__ == "__main__":
    start_scheduler()
    
    # Keep the script alive
    try:
        import time
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler stopped manually")
        print(" Scheduler stopping...")
        scheduler.shutdown()
        print(" Scheduler stopped")
