"""
End-to-End Integration Test
Flow:
signup → add task → predict → nudge → feedback → progress update
"""
import pytest
from datetime import datetime, timedelta, timezone

from backend.app.models import Student, StudentBehavior, StudentProgress, StudentPoints
from backend.src.commitment_system import CommitmentSystem
from backend.src.nudge_system import SmartNudgeSystem
from backend.src.predict import ProcrastinationPredictor
from backend.src.progress import ProgressTracker
from werkzeug.security import generate_password_hash
from backend.src.logger import logger
from backend.src.utils import safe_execute

@pytest.fixture
def test_student(session):
    student = Student(
        id=9999,
        name="Test Student",
        email="test@student.com",
        password_hash=generate_password_hash("testpassword"), 
        no_nudges=False,
        model_opt_out=False,
        created_at=datetime.now(timezone.utc)
    )
    session.add(student)
    session.commit()
    yield student
    session.delete(student)
    session.commit()

def test_full_adaptive_flow(session, test_student):
    """
    🔥 Full system integration test
    """
    logger.info("Starting end-to-end test")

    # ----------------------------
    # 1️⃣ Seed student behavior
    # ----------------------------
    behavior = StudentBehavior(
        student_id=test_student.id,
        last_minute_ratio=0.75,
        engagement_intensity=10.5,
        deadline_pressure=3.2,
        login_consistency=0.8,
        early_starter=0,
        completion_rate=0.4,
        activity_span=20.0
    )
    session.add(behavior)

    points = StudentPoints(
        student_id=test_student.id,
        total_points=50,
        current_streak=3,
        last_commitment_date=datetime.now(timezone.utc) - timedelta(days=1)
    )
    session.add(points)
    session.commit()

    # ----------------------------
    # 2️⃣ Prediction
    # ----------------------------
    predictor = ProcrastinationPredictor()
    prediction = safe_execute(predictor.predict_from_database, test_student.id, session=session)

    assert prediction is not None
    assert prediction["risk_category"] in ["low", "medium", "high"]

    logger.info(f"Prediction result: {prediction}")

    # ----------------------------
    # 3️⃣ Create commitment
    # ----------------------------
    commitment_system = CommitmentSystem()
    commitment = safe_execute(
        commitment_system.create_commitment,
        test_student.id,
        content_id=1,
        committed_datetime=datetime.now(timezone.utc) + timedelta(hours=6)
    )

    assert commitment is not None

    # ----------------------------
    # 4️⃣ Generate nudges
    # ----------------------------
    nudge_system = SmartNudgeSystem()
    nudges = safe_execute(
        nudge_system.check_and_send_nudges,
        test_student.id
    )

    assert nudges is not None
    assert isinstance(nudges, list)

    logger.info(f"Nudges generated: {nudges}")

    # ----------------------------
    # 5️⃣ Simulate task completion
    # ----------------------------
    progress = StudentProgress(
        student_id=test_student.id,
        content_id=1,
        status="completed",
        started_at=datetime.now(timezone.utc) - timedelta(hours=1),
        completed_at=datetime.now(timezone.utc)
    )
    session.add(progress)
    session.commit()

    # ----------------------------
    # 6️⃣ Update progress & streak
    # ----------------------------
    # ProgressTracker now takes the session parameter to use the same connection
    progress_tracker = ProgressTracker(session=session)
    # Since update_daily_streaks isn't implemented in the new tracker or was in ProgressTracker,
    # let's call get_stats to verify it reads progress correctly
    stats = progress_tracker.get_stats(test_student.id)
    assert stats["completed"] == 1
    assert stats["completion_rate"] == 100.0

    logger.info("End-to-end adaptive flow successful")

def test_model_opt_out_blocks_prediction(session, test_student):
    test_student.model_opt_out = True
    session.commit()

    predictor = ProcrastinationPredictor()
    result = predictor.predict_from_database(test_student.id, session=session)

    assert result["prediction"] == "disabled"
    assert result["risk_category"] is None

def test_no_nudges_mode_blocks_nudges(session, test_student):
    test_student.no_nudges = True
    session.commit()

    nudge_system = SmartNudgeSystem()
    nudges = nudge_system.check_and_send_nudges(test_student.id)

    assert nudges == []
