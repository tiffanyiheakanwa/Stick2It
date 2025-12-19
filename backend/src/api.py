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

# =========================
# Service Imports
# =========================
from predict import ProcrastinationPredictor
from recommender import AdaptiveRecommender
from progress import ProgressTracker
from commitment_system import CommitmentSystem
from nudge_system import SmartNudgeSystem
from database_setup_content import Student, get_session

# =========================
# App Configuration
# =========================
API_PREFIX = "/api/v1"

app = Flask(__name__)
CORS(app)

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

# =========================
# AUTHORIZATION GUARD
# =========================
def authorize_student(resource_student_id: int):
    current_user_id = get_jwt_identity()
    if current_user_id != resource_student_id:
        return jsonify({"error": "Unauthorized access"}), 403
    return None

# =========================
# AUTH ROUTES
# =========================

@app.route(f"{API_PREFIX}/auth/register", methods=["POST"])
def register():
    session = get_session()
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
    session = get_session()
    data = request.get_json()

    student = session.query(Student).filter_by(email=data["email"]).first()
    if not student or not student.verify_password(data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    token = create_access_token(identity=student.id)

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
    return jsonify({"student_id": get_jwt_identity()})

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
    current_user_id = get_jwt_identity()

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
    current_user_id = get_jwt_identity()

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
    data = request.get_json()
    current_user_id = get_jwt_identity()

    commit_time = datetime.fromisoformat(data["committed_datetime"])

    return jsonify(
        commitment_system.create_commitment(
            student_id=current_user_id,
            content_id=data["content_id"],
            committed_datetime=commit_time,
            commitment_type=data.get("type", "start_time")
        )
    )


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
# ACCOUNTABILITY PARTNER
# =========================

@app.route(f"{API_PREFIX}/partners", methods=["POST"])
@jwt_required()
def add_partner():
    data = request.get_json()
    current_user_id = get_jwt_identity()

    return jsonify(
        commitment_system.add_accountability_partner(
            student_id=current_user_id,
            partner_name=data["partner_name"],
            partner_email=data.get("partner_email"),
            partner_phone=data.get("partner_phone")
        )
    )

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
# ENTRY POINT
# =========================

if __name__ == "__main__":
    from scheduler import start_scheduler

    start_scheduler()   # ✅ start background jobs first

    print("\n🚀 Stick2It API running")
    print("📍 Base URL: http://localhost:5000/api/v1")

    app.run(debug=True, host="0.0.0.0", port=5000)
