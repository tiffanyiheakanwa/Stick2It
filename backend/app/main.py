from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, Depends, HTTPException, Body, Security, Request, Path
from fastapi_utilities import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager

from datetime import datetime, timedelta, timezone
from itsdangerous import SignatureExpired, BadSignature
import traceback
import time

from backend.src.nudge_system import SmartNudgeSystem
from backend.src.logger import logger
from backend.src.commitment_system import CommitmentSystem
from backend.src.predict import ProcrastinationPredictor
from backend.src.recommender import AdaptiveRecommender
from backend.src.progress import ProgressTracker
from backend.src.scheduler import start_scheduler
from backend.src.feedback_loop import MLFeedbackLoop

from backend.app.database import get_db_session, SessionLocal
from backend.app.models import Student, Commitment, Notification, Prediction, StudentPoints
from backend.app.config import serializer, SECURITY_SALT
from .tasks import process_student_nudge_task, evolve_ai_model
from backend.src.ingestion import AssignmentIngestor
from ..src.database_setup import engine, Base 

Base.metadata.create_all(bind=engine)
# =========================
# Auth & Security Helpers
# =========================
import os
import jwt
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from backend.app.config import SECRET_KEY
security = HTTPBearer()

_risk_cache = {}
RISK_CACHE_TTL = 300  # 5 minutes

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)) -> int:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return int(user_id_str)
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def authorize_student(student_id: int = Path(...), current_user_id: int = Depends(get_current_user)):
    if current_user_id != student_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    return current_user_id

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown events."""
    # Startup
    start_scheduler()
    logger.info("Scheduler started on API startup.")
    _run_nudge_monitoring()
    yield
    # Shutdown (add cleanup here if needed)

app = FastAPI(lifespan=lifespan)

# =========================
# Initialize Core Systems (ONCE)
# =========================
try:
    predictor = ProcrastinationPredictor()
    recommender = AdaptiveRecommender()
    progress_tracker = ProgressTracker()
    commitment_manager = CommitmentSystem()
    nudge_service = SmartNudgeSystem()
    logger.info("Core systems loaded successfully in FastAPI")
except Exception as e:
    raise RuntimeError(f"Startup failure: {e}")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://remindai.onrender.com",
    os.getenv("FRONTEND_URL", "https://remindai.onrender.com"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          
    allow_credentials=True,
    allow_methods=["*"],           
    allow_headers=["*"],             
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, WebSocket] = {}

    async def connect(self, student_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[student_id] = websocket

    def disconnect(self, student_id: int):
        if student_id in self.active_connections:
            del self.active_connections[student_id]

    async def send_personal_message(self, message: dict, student_id: int):
        if student_id in self.active_connections:
            await self.active_connections[student_id].send_json(message)

manager = ConnectionManager()

def notify_admins(error_message: str):
    logger.critical(f" ADMIN ALERT: Nudge Cycle Failure: {error_message}")

@app.websocket("/ws/{student_id}")
async def websocket_endpoint(websocket: WebSocket, student_id: int):
    await manager.connect(student_id, websocket)
    try:
        while True:
            await websocket.receive_text() # Keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(student_id)

def _run_nudge_monitoring():
    """Dispatch nudge tasks to Celery for all opted-in students."""
    logger.info(" Initiating parallel nudge cycle...")
    with get_db_session() as session:
        student_ids = [
            s.id for s in session.query(Student.id).filter(Student.no_nudges == False).all()
        ]
    for s_id in student_ids:
        process_student_nudge_task.delay(s_id)
    logger.info(f" Dispatched {len(student_ids)} tasks to Celery queue.")

@repeat_every(seconds=60 * 15)
def automated_nudge_monitoring():
    _run_nudge_monitoring()

@repeat_every(seconds=60 * 60 * 24 * 7)  # Run once a week
def weekly_evolution_trigger():
    evolve_ai_model.delay()

# =========================
# AUTH ROUTES
# =========================
@app.get("/api/v1/test-cors")
async def test_cors():
    return {"ok": True}

@app.post("/api/v1/auth/register")
async def register(data: dict = Body(...)):
    with get_db_session() as session:
        email = data["email"].strip().lower()
        # 1. Check if a student with this email already exists
        existing_student = session.query(Student).filter_by(email=email).first()

        if existing_student:
            # 2. If they have a password already, it's a true conflict
            if existing_student.password_hash:
                raise HTTPException(status_code=400, detail="Email already registered")
            
            # 3. If no password exists, they likely used Google Auth. 
            # We "link" the account by setting the password now.
            existing_student.name = data.get("name", existing_student.name)
            existing_student.set_password(data["password"])
            
            # Optional: Update auth_provider to track that they now have both
            if hasattr(existing_student, 'auth_provider'):
                existing_student.auth_provider = "both"  # type: ignore[assignment]

            session.commit()
            return {
                "success": True, 
                "message": "Account linked successfully", 
                "student_id": existing_student.id
            }

        # 4. Standard registration for brand new users
        student = Student(name=data["name"], email=email)
        student.set_password(data["password"])

        # Set default provider if your model uses it
        if hasattr(student, 'auth_provider'):
            student.auth_provider = "local"  # type: ignore[assignment]

        session.add(student)
        session.commit()
        session.refresh(student)
        return {"success": True, "student_id": student.id}

@app.post("/api/v1/auth/login")
async def login(data: dict = Body(...)):
    with get_db_session() as session:
        student = session.query(Student).filter_by(email=data.get("email")).first()
        if not student or not student.verify_password(data.get("password")):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = jwt.encode({"sub": str(student.id), "exp": datetime.now(timezone.utc) + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")

        return {
            "success": True,
            "token": token,
            "student": {
                "id": student.id,
                "name": student.name,
                "email": student.email,
                "is_google_connected": bool(student.ext_access_token)
            }
        }

@app.get("/api/v1/me")
async def me(current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        student = session.get(Student, current_user_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "is_google_connected": bool(student.ext_access_token)
        }

@app.get("/api/v1/students/me/preferences")
async def get_preferences(current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        student = session.get(Student, current_user_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return {
            "success": True, 
            "nudge_preference": getattr(student, 'nudge_preference', 'auto')
        }

@app.patch("/api/v1/students/me/preferences")
async def update_preferences(data: dict = Body(...), current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        student = session.get(Student, current_user_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        pref = data.get("nudge_preference")
        if pref:
            student.nudge_preference = pref
            session.commit()
            
        return {
            "success": True,
            "message": "Preferences updated",
            "nudge_preference": student.nudge_preference
        }

@app.get("/api/v1/health")
async def health():
    return {"status": "online", "version": "1.0"}

@app.post("/api/v1/students/me/sync-assignments")
async def sync_assignments(current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        student = session.get(Student, current_user_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        ingestor = AssignmentIngestor(session)
        try:
            result = ingestor.sync_for_student(int(student.id))  # type: ignore[arg-type]
            if result.get("success"):
                return {"success": True, "synced_count": result.get("synced_count", 0)}
            elif result.get("needs_reauth"):
                raise HTTPException(status_code=401, detail=result.get("error"))
            else:
                raise HTTPException(status_code=500, detail=result.get("error"))
        except Exception as e:
            logger.error(f"Sync failed: {e}")
            raise HTTPException(status_code=500, detail="Sync operation failed")

# =========================
# GOOGLE OAUTH FLOW
# =========================
# Only for local development
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1'

import json

GOOGLE_CLIENT_SECRETS_FILE = os.path.join(os.path.dirname(__file__), "client_secret.json")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "https://stick2it.onrender.com/api/v1/auth/google/callback")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://remindai.onrender.com")
GOOGLE_REDIRECT_URI_LOCAL = os.getenv("GOOGLE_REDIRECT_URI_LOCAL", "http://localhost:8000/api/v1/auth/google/callback")
FRONTEND_URL_LOCAL = os.getenv("FRONTEND_URL_LOCAL", "http://localhost:5173")

GOOGLE_SCOPES = [
    'openid',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'https://www.googleapis.com/auth/classroom.courses.readonly',
    'https://www.googleapis.com/auth/classroom.coursework.me.readonly',
    'https://www.googleapis.com/auth/classroom.student-submissions.me.readonly'
]
OAUTH_STATE_CACHE = {}

def get_current_frontend_url(request: Request):
    if request.url.hostname in ("localhost", "127.0.0.1"):
        return FRONTEND_URL_LOCAL
    return FRONTEND_URL


def get_current_google_redirect_uri(request: Request):
    if request.url.hostname in ("localhost", "127.0.0.1"):
        return GOOGLE_REDIRECT_URI_LOCAL
    return GOOGLE_REDIRECT_URI


def get_google_flow(state=None, redirect_uri=None):
    redirect_uri = redirect_uri or GOOGLE_REDIRECT_URI
    if os.path.exists(GOOGLE_CLIENT_SECRETS_FILE):
        kwargs = dict(scopes=GOOGLE_SCOPES, redirect_uri=redirect_uri)
        if state:
            kwargs["state"] = state
        return Flow.from_client_secrets_file(GOOGLE_CLIENT_SECRETS_FILE, **kwargs)
    else:
        client_config = {
            "web": {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
        kwargs = dict(scopes=GOOGLE_SCOPES, redirect_uri=redirect_uri)
        if state:
            kwargs["state"] = state
        return Flow.from_client_config(client_config, **kwargs)

@app.get("/api/v1/auth/google")
async def google_login(request: Request):
    try:
        redirect_uri = get_current_google_redirect_uri(request)
        flow = get_google_flow(redirect_uri=redirect_uri)
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'
        )
        OAUTH_STATE_CACHE[state] = getattr(flow, 'code_verifier', None)
        return RedirectResponse(url=authorization_url)
    except Exception as e:
        logger.error(f"Google login error: {e}")
        return RedirectResponse(url=f"{FRONTEND_URL}/?error=MissingClientSecret")

@app.get("/api/v1/auth/google/callback")
async def google_callback(request: Request, state: str, code: str):
    try:
        redirect_uri = get_current_google_redirect_uri(request)
        flow = get_google_flow(state=state, redirect_uri=redirect_uri)
        code_verifier = OAUTH_STATE_CACHE.pop(state, None)
        if code_verifier:
            flow.code_verifier = code_verifier

        flow.fetch_token(code=code)
        credentials = flow.credentials

        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()  # type: ignore[attr-defined]

        email = user_info.get("email", "").lower()
        name = user_info.get("name", "Student")

        if not email:
            return RedirectResponse(url=f"{FRONTEND_URL}/?error=InvalidGoogleAccount")

        with get_db_session() as session:
            student = session.query(Student).filter_by(email=email).first()
            if not student:
                student = Student(name=name, email=email, auth_provider="google")
                session.add(student)
                session.commit()

            student.auth_provider = "google"  # type: ignore[assignment]
            student.ext_access_token = credentials.token or ""  # type: ignore[assignment]
            student.ext_refresh_token = credentials.refresh_token if credentials.refresh_token else student.ext_refresh_token
            session.commit()

            token = jwt.encode(
                {"sub": str(student.id), "exp": datetime.now(timezone.utc) + timedelta(hours=1)},
                SECRET_KEY,
                algorithm="HS256"
            )

            frontend_url = get_current_frontend_url(request)
            return RedirectResponse(url=f"{frontend_url}/?token={token}")

    except Exception as e:
        logger.error(f"Google Callback Error: {e}")
        logger.error(traceback.format_exc())
        frontend_url = get_current_frontend_url(request)
        return RedirectResponse(url=f"{frontend_url}/?error=ServerAuthError")

# =========================
# PREDICTION
# =========================
@app.post("/api/v1/predict")
async def predict_from_features(features: dict = Body(...), current_user_id: int = Depends(get_current_user)):
    return {
        "success": True,
        "prediction": predictor.predict_risk(features)
    }

@app.get("/api/v1/students/{student_id}/predict")
async def predict_for_student(student_id: int, auth: int = Depends(authorize_student)):
    return {
        "success": True,
        "prediction": predictor.predict_from_database(student_id)
    }

# =========================
# RECOMMENDATIONS
# =========================
@app.get("/api/v1/students/{student_id}/recommendations")
async def get_recommendations(student_id: int, limit: int = 5, auth: int = Depends(authorize_student)):
    return recommender.recommend(student_id, limit)

# =========================
# PROGRESS
# =========================
@app.post("/api/v1/progress/start")
async def start_content(data: dict = Body(...), current_user_id: int = Depends(get_current_user)):
    return progress_tracker.start_content(
        current_user_id,
        data.get("content_id")
    )

@app.post("/api/v1/progress/complete")
async def complete_content(data: dict = Body(...), current_user_id: int = Depends(get_current_user)):
    result = progress_tracker.complete_content(
        current_user_id,
        data.get("content_id"),
        data.get("time_spent", 0)
    )
    result["new_recommendations"] = recommender.recommend(current_user_id)  # type: ignore[index]
    with get_db_session() as session:
        MLFeedbackLoop.log_actual_outcome(session, current_user_id, data.get("content_id"), stayed_on_track=True)
    return result

@app.get("/api/v1/students/{student_id}/progress")
async def get_progress(student_id: int, auth: int = Depends(authorize_student)):
    return progress_tracker.get_stats(student_id)

# =========================
# VERIFICATION (WebSocket-backed)
# =========================
from fastapi import Form

verification_attempts = {}

@app.get("/verify/{token}", response_class=HTMLResponse)
async def buddy_verification_page(token: str, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Rate limit: max 10 requests per minute
    if client_ip in verification_attempts:
        attempts, start_time = verification_attempts[client_ip]
        if now - start_time < 60:
            if attempts >= 10:
                return "<h1>Too Many Requests</h1><p>Please try again later.</p>"
            verification_attempts[client_ip] = (attempts + 1, start_time)
        else:
            verification_attempts[client_ip] = (1, now)
    else:
        verification_attempts[client_ip] = (1, now)

    try:
        commitment_id = serializer.loads(
            token, 
            salt=SECURITY_SALT, 
            max_age=172800
        )
    except (SignatureExpired, BadSignature):
        return "<h1>Link Expired or Invalid</h1><p>This verification link is no longer valid.</p>"

    with get_db_session() as session:
        commitment = session.query(Commitment).filter(Commitment.verification_token == token).first()
        if not commitment:
            return "<h1>Link Invalid</h1>"
        if commitment.status != "pending":
            return f"<h1>Already Processed</h1>"

        return f'''
        <html>
            <body style="font-family: sans-serif; text-align: center; padding: 50px;">
                <h1>RemindAI Accountability</h1>
                <p>Did your friend complete: <strong>{commitment.assignment.title if commitment.assignment else (commitment.custom_title or "their task")}</strong>?</p>
                <div style="margin-top: 30px; display: flex; justify-content: center; gap: 20px;">
                    <a href="/verify/{token}/kept" style="padding: 15px 25px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; height: 20px; display: inline-block;">✅ Yes, they kept it!</a>
                    
                    <form action="/verify/{token}/broken" method="POST" style="margin: 0;">
                        <input type="text" name="reason" placeholder="Reason for failure (optional)" style="padding: 10px; border-radius: 5px; border: 1px solid #ccc; margin-bottom: 10px; width: 250px; display: block;" />
                        <button type="submit" style="padding: 15px 25px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px; border: none; cursor: pointer; width: 100%;">❌ No, they failed.</button>
                    </form>
                </div>
            </body>
        </html>
        '''

@app.get("/verify/{token}/kept", response_class=HTMLResponse)
async def process_kept(token: str):
    result = commitment_manager.verify_commitment(token)
    with get_db_session() as session:
        commitment = session.query(Commitment).filter(Commitment.verification_token == token).first()
        if commitment:
            MLFeedbackLoop.log_actual_outcome(
                session, 
                commitment.student_id, 
                commitment.assignment_id, 
                stayed_on_track=True
            )
            new_notif = Notification(
                recipient_id=commitment.student_id,
                message=f"Your buddy verified you kept your task '{commitment.custom_title or 'Task'}'! +{commitment.stake_value} points.",
                type="system_alert",
                status="unread"
            )
            session.add(new_notif)
            session.commit()
            
            await manager.send_personal_message(
                {"type": "COMMITMENT_UPDATED", "status": "completed", "points_gained": commitment.stake_value}, 
                int(commitment.student_id)  # type: ignore[arg-type]
            )
            predictor.refresh_behavior_stats(commitment.student_id)
                
    return f"<h1>Success!</h1><p>{result.get('message', 'Commitment verified.')}</p>"

@app.post("/verify/{token}/broken", response_class=HTMLResponse)
async def process_broken(token: str, reason: str = Form(None)):
    with get_db_session() as session:
        commitment = session.query(Commitment).filter(Commitment.verification_token == token).first()
        if commitment:
            student_id = commitment.student_id 
            commitment_manager._process_failure(session, commitment)
            MLFeedbackLoop.log_actual_outcome(session, commitment.student_id, commitment.assignment_id, stayed_on_track=False)

            fail_msg = f"Your buddy marked your task '{commitment.custom_title or 'Task'}' as failed. Penalty applied."
            if reason:
                fail_msg += f" Reason given: {reason}"

            new_notif = Notification(
                recipient_id=student_id,
                message=fail_msg,
                type="system_alert",
                status="unread"
            )
            session.add(new_notif)
            session.commit()
            
            await manager.send_personal_message(
                {"type": "COMMITMENT_UPDATED", "status": "failed"},
                int(student_id)  # type: ignore[arg-type]
            )
            predictor.refresh_behavior_stats(student_id)
            return "<h1>Penalty Executed</h1><p>The stake has been deducted. Accountability works!</p>"
    return "<h1>Error</h1><p>Commitment not found.</p>"

@app.get("/api/v1/verify/{token}")
async def get_verify_commitment_info(token: str):
    with get_db_session() as session:
        commitment = session.query(Commitment).filter(Commitment.verification_token == token).first()
        if not commitment:
            raise HTTPException(status_code=404, detail="Invalid token")
            
        return {
            "id": commitment.id,
            "title": commitment.custom_title or (commitment.assignment.title if commitment.assignment else "Task"),
            "student_name": commitment.student.name,
            "stake_type": commitment.stake_type,
            "stake_value": commitment.stake_value,
            "penalty_message": commitment.penalty_message,
            "status": commitment.status
        }

@app.post("/api/v1/verify/{token}/{action}")
async def fetch_verify_commitment(token: str, action: str):
    with get_db_session() as session:
        commitment = session.query(Commitment).filter(Commitment.verification_token == token).first()
        if not commitment:
            raise HTTPException(status_code=404, detail="Invalid token")

        if action == "kept":
            result = commitment_manager.verify_commitment(token)
            if not result.get("success"):
                raise HTTPException(status_code=400, detail=result.get("error", "Verification failed"))
            session.refresh(commitment)
            msg_status = "completed"
            points = commitment.stake_value
            MLFeedbackLoop.log_actual_outcome(session, commitment.student_id, commitment.assignment_id, stayed_on_track=True)
        elif action == "broken":
            commitment_manager._process_failure(session, commitment)
            msg_status = "failed"
            points = 0
            MLFeedbackLoop.log_actual_outcome(session, commitment.student_id, commitment.assignment_id, stayed_on_track=False)
        else:
            raise HTTPException(status_code=400, detail="Invalid action")

        student_id = commitment.student_id
        
        new_notif = Notification(
            recipient_id=student_id,
            message=f"Your buddy marked your task '{commitment.custom_title or 'Task'}' as {msg_status}.",
            type="system_alert",
            status="unread"
        )
        session.add(new_notif)
        session.commit()
        
        predictor.refresh_behavior_stats(student_id)

        await manager.send_personal_message(
            {
                "type": "COMMITMENT_UPDATED", 
                "status": msg_status,
                "points_gained": points
            }, 
            int(student_id)  # type: ignore[arg-type]
        )

        return {"success": True, "message": f"Task marked as {msg_status}"}

# =========================
# COMMITMENTS
# =========================
@app.post("/api/v1/commitments")
async def create_commitment(data: dict = Body(...), current_user_id: int = Depends(get_current_user)):
    try:
        try:
            commit_time = datetime.fromisoformat(data["committed_datetime"].replace('Z', '+00:00'))
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid date format")

        commitment = commitment_manager.create_commitment(
            student_id=current_user_id,
            committed_datetime=commit_time,
            custom_title=data.get("title"),
            buddy_name=data.get("buddy_name"),
            buddy_email=data.get("buddy_email"),
            stake_value=data.get("stake_value", 10),
            stake_type=data.get("stake_type", "Points"),
            content_id=data.get("content_id"),
            parent_commitment_id=data.get("parent_commitment_id")
        )
        
        c_id = commitment.get("commitment_id") if isinstance(commitment, dict) else commitment.id
        task_text = data.get('title') or "New Task"
        prediction_result = predictor.predict_from_task(
            task_text, 
            student_id=current_user_id,
            subjective_difficulty=data.get("subjective_difficulty", "Medium")
        )

        with get_db_session() as session:
            new_pred = Prediction(
                student_id=current_user_id,
                assignment_id=data.get('assignment_id'),
                risk_score=prediction_result['probability_high_risk'],
                predicted_at=datetime.utcnow()
            )
            session.add(new_pred)
            session.commit()

        return {"success": True, "id": c_id, "commitment_id": c_id}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=str(e))

@app.patch("/api/v1/commitments/{commit_id}/activate")
async def activate_commitment(commit_id: int, data: dict = Body(...), current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        commitment = session.get(Commitment, commit_id)
        if not commitment or commitment.student_id != current_user_id:
            raise HTTPException(status_code=404, detail="Commitment not found")
            
        if commitment.status != 'requires_stake':
            raise HTTPException(status_code=400, detail="Only unsaved assignments can be activated")

        buddy_name = data.get("buddy_name")
        stake_value = data.get("stake_value", 10)
        
        commitment.buddy_name = buddy_name  # type: ignore[assignment]
        commitment.buddy_email = data.get("buddy_email")  # type: ignore[assignment]
        commitment.stake_value = stake_value
        commitment.stake_type = data.get("stake_type", commitment.stake_type)  # type: ignore[assignment]
        commitment.status = 'pending'  # type: ignore[assignment]
        
        custom_title = commitment.assignment.title if commitment.assignment else (commitment.custom_title or "Task")
        
        # We assume `committed_datetime` maps to assignment deadline natively now.
        c_dt = commitment.committed_datetime or datetime.now(timezone.utc)
        commitment.penalty_message = f"Lose {stake_value} points if {custom_title} is not completed by {c_dt}"  # type: ignore[assignment]
        
        session.commit()
        
        commitment_manager._send_initial_buddy_alert(commitment)
        
        return {"success": True, "message": "Assignment Activated!"}

@app.patch("/api/v1/commitments/{commit_id}/start")
async def start_commitment(commit_id: int, current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        commitment = session.get(Commitment, commit_id)
        if not commitment:
            raise HTTPException(status_code=404, detail=f"Commitment {commit_id} not found")
            
        commitment.status = 'in_progress'  # type: ignore[assignment]
        commitment.started_at = datetime.now(timezone.utc)
        
        session.commit()
        predictor.refresh_behavior_stats(commitment.student_id)
        
        return {"success": True, "message": "Task started"}

@app.patch("/api/v1/commitments/{commit_id}/submit")
async def submit_commitment_for_verification(commit_id: int, current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        commitment = session.get(Commitment, commit_id)
        if not commitment or commitment.student_id != current_user_id:
            raise HTTPException(status_code=404, detail="Commitment not found")
        
        if commitment.status not in ['pending', 'in_progress']:
            raise HTTPException(status_code=400, detail="Only pending or active tasks can be submitted")

        if commitment.subtasks and any(st.status not in ['completed', 'kept'] for st in commitment.subtasks):
            raise HTTPException(status_code=400, detail="Complete all subtasks before submitting this task")
            
        if commitment.stake_type == "Social":
            commitment.status = "awaiting_verification"  # type: ignore[assignment]
            session.commit()
            
            commitment_manager._send_verification_request_alert(commitment)
            predictor.refresh_behavior_stats(current_user_id)
            
            return {"success": True, "message": "Task submitted for verification"}
        else:
            commitment.status = "completed"  # type: ignore[assignment]
            if commitment.assignment:
                commitment.assignment.status = "Completed"  # type: ignore[assignment]
            commitment.completed_at = datetime.now(timezone.utc)  # type: ignore[assignment]
            
            points = session.query(StudentPoints).filter(
                StudentPoints.student_id == current_user_id
            ).first()

            if points:
                points.total_points = points.total_points + int(commitment.stake_value)  # type: ignore[assignment]
                points.current_streak = points.current_streak + 1  # type: ignore[assignment]
                points.longest_streak = max(int(points.longest_streak), int(points.current_streak))  # type: ignore[assignment]
                points.last_commitment_date = datetime.now(timezone.utc)  # type: ignore[assignment]
                
            session.commit()
            predictor.refresh_behavior_stats(current_user_id)
            
            return {"success": True, "message": "Task completed successfully"}

@app.delete("/api/v1/commitments/{commit_id}")
async def delete_commitment(commit_id: int, current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        commitment = session.get(Commitment, commit_id)
        if not commitment or commitment.student_id != current_user_id:
            raise HTTPException(status_code=404, detail="Commitment not found")
        
        if commitment.stake_type == "Lock-in":
            raise HTTPException(status_code=403, detail="Lock-in commitments cannot be deleted.")
        
        commitment.status = "expired"  # type: ignore[assignment]
        session.commit()
        
        return {"success": True, "message": "Task ignored/deleted successfully"}

@app.get("/api/v1/buddy/commitments")
async def get_buddy_commitments(current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        student = session.get(Student, current_user_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        commitments = session.query(Commitment).filter(
            Commitment.buddy_email == student.email,
            Commitment.status.in_(['pending', 'in_progress', 'awaiting_verification'])
        ).all()

        results = []
        for c in commitments:
            prediction = session.query(Prediction).filter_by(
                student_id=c.student_id,
                assignment_id=c.assignment_id 
            ).order_by(Prediction.predicted_at.desc()).first()
            
            if not prediction and not c.assignment_id:
                # Fallback to the latest prediction for the student if it's a custom task
                prediction = session.query(Prediction).filter_by(
                    student_id=c.student_id
                ).order_by(Prediction.predicted_at.desc()).first()
            
            results.append({
                "id": c.id,
                "owner_name": c.student.name if c.student else "Unknown",
                "title": c.custom_title or (c.assignment.title if c.assignment else "Custom Task"),
                "deadline": c.committed_datetime.isoformat(),
                "stake": c.stake_value,
                "risk_score": round(float(prediction.risk_score) * 100, 1) if prediction else "N/A",  # type: ignore[arg-type]
                "verification_token": c.verification_token
            })
            
        return {"success": True, "commitments": results}

# =========================
# AI SUGGESTIONS
# =========================
from backend.src.task_ai import task_ai_service
from typing import Optional, List
from pydantic import BaseModel

class TaskBreakdownRequest(BaseModel):
    title: str
    description: Optional[str] = None

class SubtaskItem(BaseModel):
    title: str
    estimated_minutes: int

class TaskBreakdownResponse(BaseModel):
    success: bool
    subtasks: List[SubtaskItem]

@app.post("/api/v1/ai/breakdown", response_model=TaskBreakdownResponse)
async def breakdown_task_api(req: TaskBreakdownRequest, current_user_id: int = Depends(get_current_user)):
    stats = commitment_manager.get_student_stats(current_user_id)
    subtasks = task_ai_service.breakdown_task(req.title, req.description, behavioral_context=stats)
    return {"success": True, "subtasks": subtasks}

@app.post("/api/v1/interactions")
async def log_interaction(data: dict = Body(...), current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        from backend.app.models import Interaction
        interaction = Interaction(
            student_id=current_user_id,
            action_type=data.get("action_type")
        )
        session.add(interaction)
        session.commit()
        # Real-Time Trigger: Evaluate risk immediately
        process_student_nudge_task.delay(current_user_id)
        
        # Calculate new risk and push to websocket
        try:
            risk_data = predictor.predict_from_database(current_user_id)
            await manager.send_personal_message({"type": "RISK_UPDATE", "data": risk_data}, current_user_id)
        except Exception as e:
            logger.error(f"WS push failed: {e}")
        
        return {"success": True}

# =========================
# STUDENT STATS
# =========================
@app.get("/api/v1/students/{student_id}/stats")
async def get_student_stats(student_id: int, auth: int = Depends(authorize_student)):
    return commitment_manager.get_student_stats(student_id)

# =========================
# ACCOUNTABILITY PARTNER
# =========================
@app.post("/api/v1/partners")
async def add_partner(data: dict = Body(...), current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        partner_email = data.get("partner_email", "").strip().lower()

        partner = session.query(Student).filter_by(email=partner_email).first()
        if not partner:
            raise HTTPException(status_code=404, detail="User not found. They must register first.")
        
        if partner.id == current_user_id:
            raise HTTPException(status_code=400, detail="You cannot add yourself.")
        
        sender = session.get(Student, current_user_id)
        if not sender:
            raise HTTPException(status_code=404, detail="Sender not found")

        new_notif = Notification(
            recipient_id=partner.id,
            sender_id=current_user_id,
            message=f"{sender.name} wants to be your accountability buddy!",
            type="buddy_request",
            status="unread"
        )
        session.add(new_notif)
        session.commit()

        # 2. Email notification (SendGrid)
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail
            sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))
            email = Mail(
                from_email=os.getenv("FROM_EMAIL", "noreply@stick2it.com"),
                to_emails=partner.email,
                subject="You have a new accountability buddy request!",
                html_content=f"""
                    <h2>Hi {partner.name}!</h2>
                    <p><strong>{sender.name}</strong> wants to be your accountability buddy on Stick2It.</p>
                    <p>Log in to accept or decline the request.</p>
                    <a href="{FRONTEND_URL}">Open Stick2It</a>
                """
            )
            sg.send(email)
            logger.info(f"Buddy request email sent to {partner.email}")
        except Exception as e:
            logger.error(f"Email notification failed: {e}")

        # 3. Push notification (Firebase)
        try:
            import firebase_admin.messaging as fm
            if partner.fcm_token:
                message = fm.Message(
                    notification=fm.Notification(
                        title="New Buddy Request",
                        body=f"{sender.name} wants to be your accountability buddy!"
                    ),
                    token=partner.fcm_token
                )
                fm.send(message)
                logger.info(f"Push notification sent to student {partner.id}")
        except Exception as e:
            logger.error(f"Push notification failed: {e}")

        # 4. WebSocket real-time notification
        try:
            await manager.send_personal_message(
                {
                    "type": "buddy_request",
                    "message": f"{sender.name} wants to be your accountability buddy!",
                    "sender_id": current_user_id,
                    "sender_name": sender.name
                },
                int(partner.id)  # type: ignore[arg-type]
            )
        except Exception as e:
            logger.error(f"WebSocket notification failed: {e}")
            
        logger.info(f"Buddy request notification created: recipient={partner.id}, sender={current_user_id}")
        return {"success": True, "message": "Request sent to " + partner.name}

@app.get("/api/v1/partners")
async def get_partners(current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        student = session.get(Student, current_user_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        partners_list = [
            {"id": p.id, "name": p.name, "email": p.email} 
            for p in student.partners
        ]
        return {"success": True, "partners": partners_list}

# =========================
# NUDGES
# =========================
@app.get("/api/v1/students/{student_id}/nudges")
async def get_nudges(student_id: int, context: str = "dashboard", auth: int = Depends(authorize_student)):
    import time
    
    # Use cached risk score instead of recalculating every time
    cache_key = f"risk_{student_id}"
    now = time.time()
    
    if cache_key in _risk_cache and now - _risk_cache[cache_key]['ts'] < RISK_CACHE_TTL:
        current_risk = _risk_cache[cache_key]['risk']
    else:
        try:
            risk_data = predictor.predict_from_database(student_id)
            current_risk = risk_data.get('probability_high_risk', 0.5)
            _risk_cache[cache_key] = {'risk': current_risk, 'ts': now}
        except Exception:
            current_risk = 0.5

    if context == "all":
        standard_nudges = nudge_service.check_and_send_nudges(student_id)
    else:
        nudge = nudge_service.get_personalized_nudge(student_id, context)
        standard_nudges = [nudge] if nudge else []

    with get_db_session() as session:
        commitments = session.query(Commitment).filter(
            Commitment.student_id == student_id,
            Commitment.status.in_(['pending', 'in_progress'])
        ).all()
        
        ai_risk_nudges = []
        try:
            risk_data = predictor.predict_from_database(student_id)
            current_risk = risk_data.get('probability_high_risk', 0.5)
        except Exception:
            current_risk = 0.5

        if current_risk > 0.6: 
            for c in commitments:
                ai_risk_nudges.append({
                    "id": f"ai-risk-{c.id}",
                    "type": "AI_DYNAMIC_RISK",
                    "p_fail": current_risk, 
                    "message": f"High risk detected! You're likely to procrastinate on '{c.custom_title or (c.assignment.title if c.assignment else 'your task')}'.",
                    "stakeValue": c.stake_value,
                    "stakeType": c.stake_type,
                    "buddyName": c.buddy_name
                })

    combined_nudges = ai_risk_nudges + standard_nudges

    return {
        "success": True,
        "nudges": combined_nudges,
        "count": len(combined_nudges)
    }

# =========================
# NOTIFICATIONS
# =========================
@app.post("/api/v1/notifications/{notif_id}/respond")
async def respond_to_request(notif_id: int, data: dict = Body(...), current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        action = data.get("action") 
        notification = session.get(Notification, notif_id)
        
        if not notification or notification.recipient_id != current_user_id:
            raise HTTPException(status_code=404, detail="Notification not found")

        if action == "accept":
            sender = session.get(Student, notification.sender_id)
            recipient = session.get(Student, current_user_id)

            if not sender or not recipient:
                raise HTTPException(status_code=404, detail="User not found")
            
            if sender not in recipient.partners:
                recipient.partners.append(sender)
            if recipient not in sender.partners:
                sender.partners.append(recipient)
            
            notification.status = "accepted"  # type: ignore[assignment]
            
            new_notif = Notification(
                recipient_id=sender.id,
                sender_id=current_user_id,
                message=f"{recipient.name} accepted your buddy request!",
                type="system_alert",
                status="unread"
            )
            session.add(new_notif)
        else:
            notification.status = "declined"  # type: ignore[assignment]

        session.commit()
        return {"success": True}

@app.get("/api/v1/notifications")
async def get_notifications(current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        notifications = session.query(Notification).filter_by(
            recipient_id=current_user_id
        ).order_by(Notification.created_at.desc()).all()

        notifications_list = []
        for n in notifications:
            notifications_list.append({
                "id": n.id,
                "sender_id": n.sender_id,
                "message": n.message,
                "type": n.type,
                "status": n.status,
                "created_at": n.created_at.isoformat()
            })

        return {
            "success": True, 
            "notifications": notifications_list
        }

@app.post("/api/v1/students/me/fcm-token")
async def update_fcm_token(
    data: dict = Body(...), 
    current_user_id: int = Depends(get_current_user)):
    """
    Saves the Firebase token to the student's record.
    """
    token = data.get("fcm_token")
    if not token:
        raise HTTPException(status_code=400, detail="Token is required")

    with get_db_session() as session:
        student = session.query(Student).get(current_user_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        
        student.fcm_token = token
        session.commit()
        
        logger.info(f"FCM Token updated for student {current_user_id}")
        return {"success": True, "message": "Token saved successfully"}

nudge_system = SmartNudgeSystem()
import traceback

@app.get("/test-nudge")
async def test_nudge():
    db = SessionLocal()
    try:
        success = nudge_system._send_personalized_alert(
            session=db,
            student_id=2,
            nudge_type="test_manual",
            message="Hello! Your AI coach is officially online.")
        return {"status": "success", "delivered": success}
    except Exception as e:
        # This will print the exact error to your terminal
        print(traceback.format_exc()) 
        return {"status": "error", "message": str(e)}
    finally:
        db.close()

@app.get("/test-firebase-push")
async def test_push(current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        student = session.get(Student, current_user_id)
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        if not student.fcm_token:
            return {"error": "No FCM token found for this student. Log in again!"}

        # Trigger the push via our nudge system logic
        success = nudge_service._send_firebase_push(
            student.fcm_token, 
            "AI Coach: RemindAI!", 
            "Testing the push notification system. Did you see this?"
        )
        return {"push_sent": success}

@app.get("/")
def home():
    return {"message": "Backend Running - Background Monitoring Active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
