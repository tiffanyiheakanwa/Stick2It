"""
Stick2It – Hardened Flask API (v1)
Procrastination Prediction & Adaptive Intervention System
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
from datetime import datetime, timedelta

from .predict import ProcrastinationPredictor
from .recommender import AdaptiveRecommender
from .progress import ProgressTracker
from .commitment_system import CommitmentSystem
from .nudge_system import SmartNudgeSystem
from backend.app.models import Student, Commitment, Notification
from backend.app.database import get_db_session

# =========================
# App Configuration
# =========================
API_PREFIX = "/api/v1"

app = Flask(__name__)
CORS(
    app,
    resources={r"/api/*": {"origins": "http://localhost:5173"}},    
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)

app.config["JWT_SECRET_KEY"] = "SUPER_SECRET_KEY_CHANGE_THIS"
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=1)

jwt = JWTManager(app)

# =========================
# Initialize Core Systems (ONCE)
# =========================
try:
    predictor = ProcrastinationPredictor()
    recommender = AdaptiveRecommender()
    progress_tracker = ProgressTracker()
    commitment_system = CommitmentSystem()
    nudge_system = SmartNudgeSystem()
    print("✅ Core systems loaded successfully")
except Exception as e:
    raise RuntimeError(f"Startup failure: {e}")

@app.before_request
def handle_preflight():
    # Preflight requests do not carry JWT tokens. 
    # If this isn't handled, @jwt_required will block them with a 401.
    if request.method == "OPTIONS":
        res = jsonify({"status": "ok"})
        res.status_code = 200
        return res

# =========================
# AUTHORIZATION GUARD
# =========================
def authorize_student(resource_student_id: int):
    current_user_id = int(get_jwt_identity())
    if current_user_id != resource_student_id:
        return jsonify({"error": "Unauthorized access"}), 403
    return None

# =========================
# AUTH ROUTES
# =========================

@app.route("/test-cors", methods=["GET", "OPTIONS"])
def test_cors():
    return jsonify({"ok": True})
    


@app.route(f"{API_PREFIX}/auth/register", methods=["POST"])
def register():
    with get_db_session() as session:
        data = request.get_json()

        email = data["email"].strip().lower()
        if session.query(Student).filter_by(email=email).first():
            return jsonify({"error": "Email already registered"}), 400

        student = Student(name=data["name"], email=email)
        student.set_password(data["password"])

        session.add(student)
        session.commit()

        return jsonify({"success": True, "student_id": student.id})


@app.route(f"{API_PREFIX}/auth/login", methods=["POST"])
def login():
    with get_db_session() as session:
        data = request.get_json()

        student = session.query(Student).filter_by(email=data["email"]).first()
        if not student or not student.verify_password(data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        token = create_access_token(identity=str(student.id))

        return jsonify({
            "success": True,
            "token": token,
            "student": {
                "id": student.id,
                "name": student.name,
                "email": student.email
            }
        })

@app.route(f"{API_PREFIX}/me", methods=["GET"])
@jwt_required()
def me():
    return jsonify({"student_id": int(get_jwt_identity())})

# =========================
# HEALTH CHECK
# =========================

@app.route(f"{API_PREFIX}/health", methods=["GET"])
def health():
    return jsonify({"status": "online", "version": "1.0"})

# =========================
# PREDICTION
# =========================

@app.route(f"{API_PREFIX}/predict", methods=["POST"])
@jwt_required()
def predict_from_features():
    features = request.get_json()
    return jsonify({
        "success": True,
        "prediction": predictor.predict_risk(features)
    })


@app.route(f"{API_PREFIX}/students/<int:student_id>/predict", methods=["GET"])
@jwt_required()
def predict_for_student(student_id):
    auth = authorize_student(student_id)
    if auth:
        return auth

    return jsonify({
        "success": True,
        "prediction": predictor.predict_from_database(student_id)
    })

# =========================
# RECOMMENDATIONS
# =========================

@app.route(f"{API_PREFIX}/students/<int:student_id>/recommendations", methods=["GET"])
@jwt_required()
def get_recommendations(student_id):
    auth = authorize_student(student_id)
    if auth:
        return auth

    limit = request.args.get("limit", 5, type=int)
    return jsonify(recommender.recommend(student_id, limit))

# =========================
# PROGRESS
# =========================

@app.route(f"{API_PREFIX}/progress/start", methods=["POST"])
@jwt_required()
def start_content():
    data = request.get_json()
    current_user_id = int(get_jwt_identity())

    return jsonify(
        progress_tracker.start_content(
            current_user_id,
            data["content_id"]
        )
    )


@app.route(f"{API_PREFIX}/progress/complete", methods=["POST"])
@jwt_required()
def complete_content():
    data = request.get_json()
    current_user_id = int(get_jwt_identity())

    result = progress_tracker.complete_content(
        current_user_id,
        data["content_id"],
        data.get("time_spent", 0)
    )

    result["new_recommendations"] = recommender.recommend(current_user_id)
    return jsonify(result)


@app.route(f"{API_PREFIX}/students/<int:student_id>/progress", methods=["GET"])
@jwt_required()
def get_progress(student_id):
    auth = authorize_student(student_id)
    if auth:
        return auth

    return jsonify(progress_tracker.get_stats(student_id))

# =========================
# COMMITMENTS
# =========================

@app.route(f"{API_PREFIX}/commitments", methods=["POST"])
@jwt_required()
def create_commitment():
    try:
        data = request.get_json()
        current_user_id = get_jwt_identity()

        try:
            commit_time = datetime.fromisoformat(data["committed_datetime"].replace('Z', '+00:00'))
        except Exception:
            return jsonify({"error": "Invalid date format"}), 400

        return jsonify(
            commitment_system.create_commitment(
                student_id=current_user_id,
                committed_datetime=commit_time,
                custom_title=data.get("title"),
                buddy_name=data.get("buddy_name"),
                buddy_email=data.get("buddy_email"),
                stake_value=data.get("stake_value", 10),
                content_id=data.get("content_id"),
            )
        )

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 422


@app.route(f"{API_PREFIX}/commitments/<int:commitment_id>/check", methods=["POST"])
@jwt_required()
def check_commitment(commitment_id):
    return jsonify(commitment_system.check_commitment(commitment_id))


@app.route(f"{API_PREFIX}/students/<int:student_id>/stats", methods=["GET"])
@jwt_required()
def get_student_stats(student_id):
    auth = authorize_student(student_id)
    if auth:
        return auth

    return jsonify(commitment_system.get_student_stats(student_id))

# =========================
# BUDDY COMMITMENTS
# =========================
@app.route(f"{API_PREFIX}/buddy/commitments", methods=["GET"])
@jwt_required()
def get_buddy_commitments():
    with get_db_session() as session:
        current_user_id = int(get_jwt_identity())
        student = session.query(Student).get(current_user_id)
        
        # Find all commitments where the current student's email is the buddy_email
        from backend.app.models import Commitment, Prediction
        commitments = session.query(Commitment).filter_by(
            buddy_email=student.email,
            status='pending'
        ).all()

        results = []
        for c in commitments:
            # Join with Prediction to get the latest risk score
            prediction = session.query(Prediction).filter_by(
                assignment_id=c.content_id # Or the relevant link ID
            ).order_by(Prediction.predicted_at.desc()).first()
            
            results.append({
                "id": c.id,
                "owner_name": c.student.name,
                "title": c.custom_title or (c.assignment.title if c.assignment else "Custom Task"),
                "deadline": c.committed_datetime.isoformat(),
                "stake": c.stake_value,
                "risk_score": round(prediction.risk_score * 100, 1) if prediction else "N/A",
                "verification_token": c.verification_token
            })
            
        return jsonify({"success": True, "commitments": results})


# =========================
# ACCOUNTABILITY PARTNER
# =========================

@app.route(f"{API_PREFIX}/partners", methods=["POST"])
@jwt_required()
def add_partner():
    with get_db_session() as session:
        data = request.get_json()
        sender_id = int(get_jwt_identity())
        partner_email = data.get("partner_email", "").strip().lower()

        # 1. Verify the partner exists
        partner = session.query(Student).filter_by(email=partner_email).first()
        if not partner:
            return jsonify({"error": "User not found. They must register first."}), 404
        
        if partner.id == sender_id:
            return jsonify({"error": "You cannot add yourself."}), 400

        # 2. Create the Notification (Request)
        from backend.app.models import Notification # Ensure this model exists
        new_notif = Notification(
            recipient_id=partner.id,
            sender_id=sender_id,
            message=f"wants to be your accountability buddy!",
            type="buddy_request",
            status="unread"
        )
        session.add(new_notif)
        session.commit()

        return jsonify({"success": True, "message": "Request sent to " + partner.name})

@app.route(f"{API_PREFIX}/partners", methods=["GET"])
@jwt_required()
def get_partners():
    with get_db_session() as session:
        current_user_id = int(get_jwt_identity())
        student = session.query(Student).get(current_user_id)
        
        partners_list = [
            {"id": p.id, "name": p.name, "email": p.email} 
            for p in student.partners
        ]
        
        return jsonify({"success": True, "partners": partners_list})

# =========================
# NUDGES
# =========================

@app.route(f"{API_PREFIX}/students/<int:student_id>/nudges", methods=["GET"])
@jwt_required()
def get_nudges(student_id):
    auth = authorize_student(student_id)
    if auth:
        return auth

    context = request.args.get("context", "dashboard")

    if context == "all":
        nudges = nudge_system.check_and_send_nudges(student_id)
    else:
        nudge = nudge_system.get_personalized_nudge(student_id, context)
        nudges = [nudge] if nudge else []

    return jsonify({
        "success": True,
        "nudges": nudges,
        "count": len(nudges)
    })

# =========================
# NOTIFIFCATIONS
# =========================
@app.route(f"{API_PREFIX}/notifications/<int:notif_id>/respond", methods=["POST"])
@jwt_required()
def respond_to_request(notif_id):
    from backend.app.models import Notification, Student
    with get_db_session() as session:
        data = request.get_json()
        action = data.get("action") 
        current_user_id = int(get_jwt_identity())
        
        # Use session.get() for SQLAlchemy 2.0 compatibility
        notification = session.get(Notification, notif_id)
        if not notification or notification.recipient_id != current_user_id:
            return jsonify({"error": "Notification not found"}), 404

        if action == "accept":
            sender = session.get(Student, notification.sender_id)
            recipient = session.get(Student, current_user_id)
            
            # PREVENTION: Only append if the link doesn't exist
            if sender not in recipient.partners:
                recipient.partners.append(sender)
            if recipient not in sender.partners:
                sender.partners.append(recipient)
            
            notification.status = "accepted"
            
            # Send confirmation back to the requester
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
        return jsonify({"success": True})

@app.route(f"{API_PREFIX}/notifications", methods=["GET"])
@jwt_required()
def get_notifications():
    """Fetch all notifications for the current logged-in student."""
    with get_db_session() as session:
        current_user_id = int(get_jwt_identity())
        
        # Query notifications where the current user is the recipient
        # We order by created_at desc so the newest appear first
        from backend.app.models import Notification  # Ensure this is imported
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

        return jsonify({
            "success": True, 
            "notifications": notifications_list
        })

# =========================
# VERIFICATION
# =========================
@app.route(f"{API_PREFIX}/verify/<string:token>/<string:action>", methods=["POST"])
def verify_commitment(token, action):
    with get_db_session() as session:
        commitment = session.query(Commitment).filter_by(verification_token=token).first()
        if not commitment:
            return jsonify({"error": "Invalid token"}), 404
            
        if action == "kept":
            commitment.status = "completed"
            commitment.is_verified_by_buddy = True
        elif action == "broken":
            commitment.status = "failed"
            
        session.commit()
        return jsonify({"success": True})

# =========================
# ENTRY POINT
# =========================

if __name__ == "__main__":
    from .scheduler import start_scheduler

    start_scheduler()   # ✅ start background jobs first

    print("\n🚀 Stick2It API running")
    print("📍 Base URL: http://localhost:5000/api/v1")

    app.run(debug=True, host="0.0.0.0", port=5000)
