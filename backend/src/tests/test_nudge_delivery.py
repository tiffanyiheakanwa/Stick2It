"""
Nudge Delivery Tests
Verifies that:
  1. In-app Notification rows are written to the DB when a nudge is sent.
  2. Nudge rows are written to the DB.
  3. The SendGrid email helper is called with the right arguments.
  4. Streak-protection nudges also persist a Notification row.
  5. No duplicate nudges are sent within the 24-h cooldown window.
  6. No nudges fire for opted-out students.

Architecture note:
  SmartNudgeSystem.check_and_send_nudges opens its own get_db_session()
  internally (not the pytest-injected test session), so all assertions query
  via a fresh session from the same SessionLocal to see committed data.
"""
import pytest
from unittest.mock import patch
from datetime import datetime, timedelta, timezone
import itertools

from werkzeug.security import generate_password_hash

from backend.app.models import (
    Student, StudentPoints, StudentBehavior,
    Commitment, Assignment, Nudge, Notification,
)
from backend.app.database import SessionLocal
from backend.src.nudge_system import SmartNudgeSystem

# ---------------------------------------------------------------------------
# Unique ID generator — avoids UNIQUE constraint collisions between tests
# ---------------------------------------------------------------------------
_id_counter = itertools.count(start=8000)

def _next_id():
    return next(_id_counter)


# ---------------------------------------------------------------------------
# Low-level DB helpers (use SessionLocal directly so we share the same DB
# that the nudge system's internal get_db_session() uses)
# ---------------------------------------------------------------------------

def _fresh_session():
    return SessionLocal()


def _make_student(sid, email):
    db = _fresh_session()
    try:
        student = Student(
            id=sid,
            name="Nudge Tester",
            email=email,
            password_hash=generate_password_hash("pw"),
            no_nudges=False,
            model_opt_out=False,
            experimental_group=False,   # control group — simple time-pressure rule
            created_at=datetime.now(timezone.utc),
        )
        db.add(student)

        points = StudentPoints(
            student_id=sid,
            total_points=80,
            current_streak=5,
            # last activity was 2 days ago — streak is at risk
            last_commitment_date=datetime.now(timezone.utc) - timedelta(days=2),
        )
        db.add(points)

        behavior = StudentBehavior(
            student_id=sid,
            last_minute_ratio=0.8,
            engagement_intensity=12.0,
            deadline_pressure=4.0,
            login_consistency=0.7,
            early_starter=0,
            completion_rate=0.4,
            activity_span=18.0,
            last_login=datetime.now(timezone.utc) - timedelta(days=2),
        )
        db.add(behavior)
        db.commit()
    finally:
        db.close()


def _make_commitment(sid):
    """Create an assignment due in 12 h + a 'pending' commitment for it."""
    db = _fresh_session()
    try:
        assignment = Assignment(
            title="Test Assignment",
            description="desc",
            due_date=datetime.now(timezone.utc) + timedelta(hours=12),
            student_id=sid,
            status="Pending",
        )
        db.add(assignment)
        db.flush()

        commitment = Commitment(
            student_id=sid,
            assignment_id=assignment.id,
            stake_type="Points",
            stake_value=20,
            penalty_message="Lose 20 points",
            buddy_name="Buddy",
            buddy_email="buddy@example.com",
            status="pending",
            committed_datetime=datetime.now(timezone.utc) + timedelta(hours=12),
            created_at=datetime.now(timezone.utc),
        )
        db.add(commitment)
        db.commit()
    finally:
        db.close()


def _cleanup(sid):
    """Delete all test data for a given student_id."""
    db = _fresh_session()
    try:
        db.query(Notification).filter(Notification.recipient_id == sid).delete()
        db.query(Nudge).filter(Nudge.student_id == sid).delete()
        db.query(Commitment).filter(Commitment.student_id == sid).delete()
        db.query(Assignment).filter(Assignment.student_id == sid).delete()
        db.query(StudentBehavior).filter(StudentBehavior.student_id == sid).delete()
        db.query(StudentPoints).filter(StudentPoints.student_id == sid).delete()
        db.query(Student).filter(Student.id == sid).delete()
        db.commit()
    finally:
        db.close()


def _query_notifications(sid):
    db = _fresh_session()
    try:
        return db.query(Notification).filter(
            Notification.recipient_id == sid,
            Notification.type == "nudge"
        ).all()
    finally:
        db.close()


def _query_nudges(sid):
    db = _fresh_session()
    try:
        return db.query(Nudge).filter(Nudge.student_id == sid).all()
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Test 1 — In-app Notification is persisted after a nudge fires
# ---------------------------------------------------------------------------

def test_in_app_notification_persisted():
    """
    When check_and_send_nudges fires, a Notification row with type='nudge'
    must be committed to the DB for the target student.
    """
    sid = _next_id()
    email = f"nudge_notif_{sid}@test.com"
    _make_student(sid, email)
    _make_commitment(sid)

    ns = SmartNudgeSystem()
    with patch.object(ns.predictor, "predict_from_database",
                      return_value={"risk_score": 50}), \
         patch("backend.src.nudge_system.send_sendgrid_email", return_value=True):
        ns.check_and_send_nudges(sid)

    try:
        notifications = _query_notifications(sid)
        assert len(notifications) >= 1, (
            "Expected ≥1 Notification row with type='nudge' but found none.\n"
            "Check that _send_personalized_alert calls session.commit()."
        )
        assert notifications[0].status == "unread"
        assert notifications[0].message
    finally:
        _cleanup(sid)


# ---------------------------------------------------------------------------
# Test 2 — Nudge row is persisted in the nudges table
# ---------------------------------------------------------------------------

def test_nudge_row_persisted():
    """A Nudge record must be written for ML training data."""
    sid = _next_id()
    email = f"nudge_row_{sid}@test.com"
    _make_student(sid, email)
    _make_commitment(sid)

    ns = SmartNudgeSystem()
    with patch.object(ns.predictor, "predict_from_database",
                      return_value={"risk_score": 50}), \
         patch("backend.src.nudge_system.send_sendgrid_email", return_value=True):
        ns.check_and_send_nudges(sid)

    try:
        nudges = _query_nudges(sid)
        assert len(nudges) >= 1, (
            "Expected ≥1 Nudge row but found none.\n"
            "session.commit() may be missing in _send_personalized_alert."
        )
        assert nudges[0].nudge_type
        assert nudges[0].message
    finally:
        _cleanup(sid)


# ---------------------------------------------------------------------------
# Test 3 — SendGrid email is called with the correct address
# ---------------------------------------------------------------------------

def test_email_called_with_correct_address():
    """send_sendgrid_email must be invoked with the student's email."""
    sid = _next_id()
    email = f"nudge_email_{sid}@test.com"
    _make_student(sid, email)
    _make_commitment(sid)

    ns = SmartNudgeSystem()
    with patch.object(ns.predictor, "predict_from_database",
                      return_value={"risk_score": 50}), \
         patch("backend.src.nudge_system.send_sendgrid_email",
               return_value=True) as mock_email:
        ns.check_and_send_nudges(sid)

    try:
        assert mock_email.called, (
            "send_sendgrid_email was never called.\n"
            "Check the routing logic in _send_personalized_alert."
        )
        # First positional arg is to_email
        sent_to = mock_email.call_args[0][0]
        assert sent_to == email, (
            f"Email was sent to '{sent_to}' instead of '{email}'"
        )
    finally:
        _cleanup(sid)


# ---------------------------------------------------------------------------
# Test 4 — Streak-protection nudge persists Notification
# ---------------------------------------------------------------------------

def test_streak_protection_persists_notification():
    """
    trigger_streak_protection_cycle must persist a Notification row
    for a student with a 3+ day streak who hasn't acted today.
    """
    sid = _next_id()
    email = f"streak_{sid}@test.com"
    _make_student(sid, email)

    ns = SmartNudgeSystem()
    with patch("backend.src.nudge_system.send_sendgrid_email", return_value=True):
        ns.trigger_streak_protection_cycle(sid)

    try:
        notifications = _query_notifications(sid)
        assert len(notifications) >= 1, (
            "Streak-protection nudge did not create a Notification row.\n"
            "Check _send_personalized_alert commits the session."
        )
    finally:
        _cleanup(sid)


# ---------------------------------------------------------------------------
# Test 5 — Duplicate nudges are blocked by the 24-h cooldown
# ---------------------------------------------------------------------------

def test_no_duplicate_nudges_within_cooldown():
    """
    Calling check_and_send_nudges twice on the same SmartNudgeSystem instance
    should only create ONE Nudge row because sent_cache blocks re-sending.
    """
    sid = _next_id()
    email = f"dedup_{sid}@test.com"
    _make_student(sid, email)
    _make_commitment(sid)

    ns = SmartNudgeSystem()
    with patch.object(ns.predictor, "predict_from_database",
                      return_value={"risk_score": 50}), \
         patch("backend.src.nudge_system.send_sendgrid_email", return_value=True):
        ns.check_and_send_nudges(sid)
        ns.check_and_send_nudges(sid)   # second call — should be blocked

    try:
        nudges = _query_nudges(sid)
        assert len(nudges) == 1, (
            f"Expected 1 nudge (duplicate blocked), but got {len(nudges)}.\n"
            "Check _mark_sent is called and _can_send respects the cooldown."
        )
    finally:
        _cleanup(sid)


# ---------------------------------------------------------------------------
# Test 6 — No nudges sent when student has opted out
# ---------------------------------------------------------------------------

def test_no_nudges_when_opted_out():
    """Students with no_nudges=True must receive nothing."""
    sid = _next_id()
    email = f"optout_{sid}@test.com"

    db = _fresh_session()
    try:
        opted_out = Student(
            id=sid,
            name="Opted Out",
            email=email,
            password_hash=generate_password_hash("pw"),
            no_nudges=True,
            model_opt_out=False,
            experimental_group=False,
            created_at=datetime.now(timezone.utc),
        )
        db.add(opted_out)
        db.commit()
    finally:
        db.close()

    ns = SmartNudgeSystem()
    with patch("backend.src.nudge_system.send_sendgrid_email",
               return_value=True) as mock_email:
        result = ns.check_and_send_nudges(sid)

    try:
        assert result == [], "Opted-out student should receive no nudges"
        mock_email.assert_not_called()
        assert len(_query_nudges(sid)) == 0
        assert len(_query_notifications(sid)) == 0
    finally:
        _cleanup(sid)
