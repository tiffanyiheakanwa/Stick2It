from fastapi import FastAPI
from fastapi_utilities import repeat_every
from backend.src.nudge_system import SmartNudgeSystem
from backend.src.logger import logger
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from backend.src.commitment_system import CommitmentSystem
from backend.app.database import get_db_session
from backend.app.models import Student, Commitment
from itsdangerous import SignatureExpired, BadSignature
from backend.app.config import serializer, SECURITY_SALT
import time

app = FastAPI()
nudge_service = SmartNudgeSystem()
router = APIRouter()
commitment_manager = CommitmentSystem()

def notify_admins(error_message: str):
    """
    Alerting logic: Replace this with an actual email, 
    Slack webhook, or monitoring service (e.g., Sentry).
    """
    logger.critical(f"🚨 ADMIN ALERT: Nudge Cycle Failure: {error_message}")
    # Example: send_admin_email("Nudge System Error", error_message)

@app.on_event("startup")
@repeat_every(seconds=60 * 60)  # Run every 1 hour
def automated_nudge_monitoring():
    logger.info("🚀 Starting background nudge monitoring cycle...")
    
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            with get_db_session() as session:
                student_ids = [s.id for s in session.query(Student.id).filter(Student.no_nudges == False).all()]                
                for s_id in student_ids:
                    try:
                        nudge_service.check_and_send_nudges(s_id)
                        nudge_service.trigger_streak_protection_cycle(s_id)
                    except Exception as student_error:
                        # Log individual student failures but continue the cycle
                        logger.error(f"❌ Error for student {s_id}: {student_error}")
            
            logger.info("✅ Background nudge monitoring cycle complete.")
            break  # Success! Exit the retry loop.

        except Exception as cycle_error:
            # Handle transient DB or system errors
            logger.warning(f"⚠️ Attempt {attempt + 1} failed: {cycle_error}")
            
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))  # Exponential backoff
            else:
                # Critical failure after all retries
                error_details = f"All {max_retries} attempts failed. Last error: {str(cycle_error)}"
                notify_admins(error_details)

# --- NEW BUDDY ROUTE ---
@app.get("/verify/{token}", response_class=HTMLResponse)
async def buddy_verification_page(token: str):
    try:
        commitment_id = serializer.loads(
            token, 
            salt=SECURITY_SALT, 
            max_age=172800  # 48 hours in seconds
        )
    except (SignatureExpired, BadSignature):
        return "<h1>Link Expired or Invalid</h1><p>This verification link is no longer valid.</p>"

    with get_db_session() as session:
        # Check if the token exists
        commitment = session.query(Commitment).filter(Commitment.verification_token == token).first()
        
        if not commitment:
            return "<h1>Link Invalid</h1><p>This verification link is incorrect or has expired.</p>"

        if commitment.status != "pending":
            return f"<h1>Already Processed</h1><p>This commitment was already marked as {commitment.status}.</p>"

        # Simple HTML Interface for the Buddy
        return f"""
        <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>Stick2It Accountability</h1>
                <p>Did your friend complete: <strong>{commitment.assignment.title}</strong>?</p>
                <div style="margin-top: 30px;">
                    <a href="/verify/{token}/kept" style="padding: 15px 25px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin-right: 10px;">✅ Yes, they kept it!</a>
                    <a href="/verify/{token}/broken" style="padding: 15px 25px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px;">❌ No, they failed.</a>
                </div>
            </body>
        </html>
        """

@app.get("/verify/{token}/kept", response_class=HTMLResponse)
async def process_kept(token: str):
    result = commitment_manager.verify_commitment(token)
    return f"<h1>Success!</h1><p>{result.get('message', 'Commitment verified.')}</p>"

@app.get("/verify/{token}/broken", response_class=HTMLResponse)
async def process_broken(token: str):
    with get_db_session() as session:
        commitment = session.query(Commitment).filter(Commitment.verification_token == token).first()
        if commitment:
            commitment_manager._process_failure(session, commitment)
            return "<h1>Penalty Executed</h1><p>The stake has been deducted. Accountability works!</p>"
    return "<h1>Error</h1><p>Commitment not found.</p>"

@app.get("/")
def home():
    return {"message": "Backend Running - Background Monitoring Active"}