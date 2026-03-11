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
        print(f"⏰ [{datetime.utcnow()}] Checking commitments...")
        logger.info("⏰ Running job: check_commitments")
        safe_execute(commitment_system.check_all_commitments())
    except Exception as e:
        print(f"❌ Error in check_commitments: {e}")
        logger.error(f"❌ Error in check_commitments: {e}")
        traceback.print_exc()

def send_nudges():
    """Run nudge engine to send personalized nudges"""
    try:
        print(f"🔔 [{datetime.utcnow()}] Running nudge engine...")
        logger.info("🔔 Running job: send_nudges")
        safe_execute(nudge_system.run_global_nudge_cycle())
    except Exception as e:
        print(f"❌ Error in send_nudges: {e}")
        logger.error(f"❌ Error in send_nudges: {e}")
        traceback.print_exc()

def update_streaks():
    """Update daily streaks for all students"""
    try:
        print(f"🔥 [{datetime.utcnow()}] Updating daily streaks...")
        logger.info("🔥 Running job: update_streaks")
        safe_execute(progress_tracker.update_daily_streaks)
    except Exception as e:
        print(f"❌ Error in update_streaks: {e}")
        traceback.print_exc()

def protect_streaks():
    """NEW: Specific check for students at risk of losing streaks."""
    try:
        logger.info("🔥 Running job: protect_streaks")
        # Logic triggers specifically for 'Streak at Risk' nudges
        safe_execute(nudge_system.trigger_streak_protection_cycle())
    except Exception as e:
        logger.error(f"❌ Error in protect_streaks: {e}")

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
        logger.info("✅ Scheduler started successfully")
        print("✅ Scheduler started")
        print("📅 Jobs scheduled:")
        for job in scheduler.get_jobs():
            print(f" - {job.id} next run at {job.next_run_time}")
    except Exception as e:
        logger.error(f"❌ Failed to start scheduler: {e}")
        logger.error("Scheduler will retry on next launch")
        print(f"❌ Failed to start scheduler: {e}")
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
        print("🛑 Scheduler stopping...")
        scheduler.shutdown()
        print("✅ Scheduler stopped")
