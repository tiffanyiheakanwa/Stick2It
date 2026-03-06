from fastapi import FastAPI
from fastapi_utils.tasks import repeat_every
from backend.src.nudge_system import SmartNudgeSystem
from backend.src.logger import logger
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from backend.src.commitment_system import CommitmentSystem
from backend.app.database import get_db_session
from backend.app.models import Student, Commitment

app = FastAPI()
nudge_service = SmartNudgeSystem()
router = APIRouter()
commitment_manager = CommitmentSystem()

# --- NEW BUDDY ROUTE ---
@app.get("/verify/{token}", response_class=HTMLResponse)
async def buddy_verification_page(token: str):
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

@app.on_event("startup")
@repeat_every(seconds=60 * 60)  # Run every 1 hour
def automated_nudge_monitoring():
    """
    Background task that iterates through all students to check 
    risk levels and send JIT (Just-in-Time) nudges.
    """
    logger.info("🚀 Starting background nudge monitoring cycle...")
    
    with get_db_session() as session:
        # Fetch all students who haven't opted out of nudges
        students = session.query(Student).filter(Student.no_nudges == False).all()
        
        for student in students:
            try:
                # 1. Check for behavioral risks and send dynamic nudges
                nudge_service.check_and_send_nudges(student.id)
                
                # 2. Specifically check for streaks at risk (Loss Aversion)
                nudge_service.trigger_streak_protection_cycle(student.id)
                
            except Exception as e:
                logger.error(f"❌ Error during background nudge for student {student.id}: {e}")

    logger.info("✅ Background nudge monitoring cycle complete.")

@app.get("/")
def home():
    return {"message": "Backend Running - Background Monitoring Active"}