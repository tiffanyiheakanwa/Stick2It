from fastapi import FastAPI, WebSocket, WebSocketDisconnect, APIRouter, Depends, HTTPException, Body, Security, Request, Path
from fastapi_utilities import repeat_every
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import HTMLResponse

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

from backend.app.database import get_db_session
from backend.app.models import Student, Commitment, Notification, Prediction
from backend.app.config import serializer, SECURITY_SALT
from .tasks import process_student_nudge_task

# =========================
# Auth & Security Helpers
# =========================
import jwt
SECRET_KEY = "SUPER_SECRET_KEY_CHANGE_THIS"
security = HTTPBearer()

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

app = FastAPI()

# =========================
# Initialize Core Systems (ONCE)
# =========================
try:
    predictor = ProcrastinationPredictor()
    recommender = AdaptiveRecommender()
    progress_tracker = ProgressTracker()
    commitment_manager = CommitmentSystem()
    nudge_service = SmartNudgeSystem()
    logger.info("✅ Core systems loaded successfully in FastAPI")
except Exception as e:
    raise RuntimeError(f"Startup failure: {e}")

origins = [
    "http://localhost:5173",  
    "http://127.0.0.1:5173",
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

@app.on_event("startup")
def startup_event():
    start_scheduler()
    logger.info("Scheduler started on API startup.")

@app.on_event("startup")
@repeat_every(seconds=60 * 60)
def automated_nudge_monitoring():
    logger.info(" Initiating parallel nudge cycle...")
    
    with get_db_session() as session:
        student_ids = [
            s.id for s in session.query(Student.id).filter(Student.no_nudges == False).all()
        ]
    
    for s_id in student_ids:
        process_student_nudge_task.delay(s_id)
    
    logger.info(f" Dispatched {len(student_ids)} tasks to Celery queue.")

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
        if session.query(Student).filter_by(email=email).first():
            raise HTTPException(status_code=400, detail="Email already registered")

        student = Student(name=data["name"], email=email)
        student.set_password(data["password"])

        session.add(student)
        session.commit()
        return {"success": True, "student_id": student.id}

@app.post("/api/v1/auth/login")
async def login(data: dict = Body(...)):
    with get_db_session() as session:
        student = session.query(Student).filter_by(email=data.get("email")).first()
        if not student or not student.verify_password(data.get("password")):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = jwt.encode({"sub": str(student.id), "exp": datetime.utcnow() + timedelta(hours=1)}, SECRET_KEY, algorithm="HS256")

        return {
            "success": True,
            "token": token,
            "student": {
                "id": student.id,
                "name": student.name,
                "email": student.email
            }
        }

@app.get("/api/v1/me")
async def me(current_user_id: int = Depends(get_current_user)):
    return {"student_id": current_user_id}

@app.get("/api/v1/health")
async def health():
    return {"status": "online", "version": "1.0"}

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
    result["new_recommendations"] = recommender.recommend(current_user_id)
    return result

@app.get("/api/v1/students/{student_id}/progress")
async def get_progress(student_id: int, auth: int = Depends(authorize_student)):
    return progress_tracker.get_stats(student_id)

# =========================
# VERIFICATION (WebSocket-backed)
# =========================
@app.get("/verify/{token}", response_class=HTMLResponse)
async def buddy_verification_page(token: str):
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
                <h1>Stick2It Accountability</h1>
                <p>Did your friend complete: <strong>{commitment.assignment.title if commitment.assignment else (commitment.custom_title or "their task")}</strong>?</p>
                <div style="margin-top: 30px;">
                    <a href="/verify/{token}/kept" style="padding: 15px 25px; background: #28a745; color: white; text-decoration: none; border-radius: 5px; margin-right: 10px;"> Yes, they kept it!</a>
                    <a href="/verify/{token}/broken" style="padding: 15px 25px; background: #dc3545; color: white; text-decoration: none; border-radius: 5px;"> No, they failed.</a>
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
                commitment.student_id
            )
            predictor.refresh_behavior_stats(commitment.student_id)
                
    return f"<h1>Success!</h1><p>{result.get('message', 'Commitment verified.')}</p>"

@app.get("/verify/{token}/broken", response_class=HTMLResponse)
async def process_broken(token: str):
    with get_db_session() as session:
        commitment = session.query(Commitment).filter(Commitment.verification_token == token).first()
        if commitment:
            student_id = commitment.student_id 
            commitment_manager._process_failure(session, commitment)
            
            new_notif = Notification(
                recipient_id=student_id,
                message=f"Your buddy marked your task '{commitment.custom_title or 'Task'}' as failed. Penalty applied.",
                type="system_alert",
                status="unread"
            )
            session.add(new_notif)
            session.commit()
            
            await manager.send_personal_message(
                {"type": "COMMITMENT_UPDATED", "status": "failed"}, 
                student_id
            )
            predictor.refresh_behavior_stats(student_id)
            return "<h1>Penalty Executed</h1><p>The stake has been deducted. Accountability works!</p>"
    return "<h1>Error</h1><p>Commitment not found.</p>"

@app.post("/api/v1/verify/{token}/{action}")
async def fetch_verify_commitment(token: str, action: str):
    with get_db_session() as session:
        commitment = session.query(Commitment).filter(Commitment.verification_token == token).first()
        if not commitment:
            raise HTTPException(status_code=404, detail="Invalid token")

        if action == "kept":
            commitment.status = "completed"
            commitment.is_verified_by_buddy = True
            msg_status = "completed"
            points = commitment.stake_value
        elif action == "broken":
            commitment_manager._process_failure(session, commitment)
            msg_status = "failed"
            points = 0
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
            student_id
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
            content_id=data.get("content_id"),
        )
        
        c_id = commitment.get("id") if isinstance(commitment, dict) else commitment.id
        task_text = data.get('title') or "New Task"
        prediction_result = predictor.predict_from_task(task_text, student_id=current_user_id)

        with get_db_session() as session:
            new_pred = Prediction(
                student_id=current_user_id,
                assignment_id=data.get('assignment_id'),
                risk_score=prediction_result['probability_high_risk'],
                predicted_at=datetime.utcnow()
            )
            session.add(new_pred)
            session.commit()

        return {"success": True, "id": c_id}
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=422, detail=str(e))

@app.patch("/api/v1/commitments/{commit_id}/start")
async def start_commitment(commit_id: int, current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        commitment = session.get(Commitment, commit_id)
        if not commitment:
            raise HTTPException(status_code=404, detail=f"Commitment {commit_id} not found")
            
        commitment.status = 'in_progress'
        commitment.started_at = datetime.now(timezone.utc)
        
        session.commit()
        predictor.refresh_behavior_stats(commitment.student_id)
        
        return {"success": True, "message": "Task started"}

@app.get("/api/v1/buddy/commitments")
async def get_buddy_commitments(current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        student = session.get(Student, current_user_id)
        commitments = session.query(Commitment).filter_by(
            buddy_email=student.email,
            status='pending'
        ).all()

        results = []
        for c in commitments:
            prediction = session.query(Prediction).filter_by(
                assignment_id=c.content_id 
            ).order_by(Prediction.predicted_at.desc()).first()
            
            results.append({
                "id": c.id,
                "owner_name": c.student.name if c.student else "Unknown",
                "title": c.custom_title or (c.assignment.title if c.assignment else "Custom Task"),
                "deadline": c.committed_datetime.isoformat(),
                "stake": c.stake_value,
                "risk_score": round(prediction.risk_score * 100, 1) if prediction else "N/A",
                "verification_token": c.verification_token
            })
            
        return {"success": True, "commitments": results}

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

        new_notif = Notification(
            recipient_id=partner.id,
            sender_id=current_user_id,
            message=f"wants to be your accountability buddy!",
            type="buddy_request",
            status="unread"
        )
        session.add(new_notif)
        session.commit()

        return {"success": True, "message": "Request sent to " + partner.name}

@app.get("/api/v1/partners")
async def get_partners(current_user_id: int = Depends(get_current_user)):
    with get_db_session() as session:
        student = session.query(Student).get(current_user_id)
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
    if context == "all":
        standard_nudges = nudge_service.check_and_send_nudges(student_id)
    else:
        nudge = nudge_service.get_personalized_nudge(student_id, context)
        standard_nudges = [nudge] if nudge else []

    with get_db_session() as session:
        commitments = session.query(Commitment).filter_by(
            student_id=student_id, 
            status='pending'
        ).all()
        
        ai_risk_nudges = []
        for c in commitments:
            pred = session.query(Prediction).filter_by(
                student_id=student_id,
                assignment_id=c.assignment_id
            ).order_by(Prediction.predicted_at.desc()).first()
            
            if pred and pred.risk_score > 0.6: 
                ai_risk_nudges.append({
                    "id": f"ai-risk-{c.id}",
                    "type": "AI_DYNAMIC_RISK",
                    "p_fail": pred.risk_score, 
                    "message": f"High risk detected! You're likely to procrastinate on '{c.custom_title or 'your task'}'.",
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
            
            if sender not in recipient.partners:
                recipient.partners.append(sender)
            if recipient not in sender.partners:
                sender.partners.append(recipient)
            
            notification.status = "accepted"
            
            new_notif = Notification(
                recipient_id=sender.id,
                sender_id=current_user_id,
                message=f"{recipient.name} accepted your buddy request!",
                type="system_alert",
                status="unread"
            )
            session.add(new_notif)
        else:
            notification.status = "declined"

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

@app.get("/")
def home():
    return {"message": "Backend Running - Background Monitoring Active"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)