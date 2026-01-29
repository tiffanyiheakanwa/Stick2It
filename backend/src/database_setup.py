from sqlalchemy import (
    create_engine, Column, Integer, Float, String, Boolean,
    DateTime, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

# ---------------------------
# Flexible engine creation
# ---------------------------
def get_engine(db_url="sqlite:///procrastination.db"):
    return create_engine(db_url, connect_args={"check_same_thread": False})

# Default engine and session
engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()

# -------------------------------------------------------------
# STUDENT MODEL
# -------------------------------------------------------------
class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True)
    id_student = Column(Integer, unique=True)

    name = Column(String(100))
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    final_result = Column(String(20))
    is_active = Column(Boolean, default=True)
    model_opt_out = Column(Boolean, default=False)
    no_nudges = Column(Boolean, default=False)
    
    # Relationships
    tasks = relationship("Task", back_populates="student")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# -------------------------------------------------------------
# STUDENT BEHAVIOR
# -------------------------------------------------------------
class StudentBehavior(Base):
    __tablename__ = 'behaviors'

    id = Column(Integer, primary_key=True)
    id_student = Column(Integer)

    last_minute_ratio = Column(Float)
    engagement_intensity = Column(Float)
    deadline_pressure = Column(Float)
    login_consistency = Column(Float)
    early_starter = Column(Integer)
    completion_rate = Column(Float)
    activity_span = Column(Float)

    high_risk = Column(Boolean)

    num_login_days = Column(Integer)
    total_clicks = Column(Integer)
    avg_score = Column(Float)

# -------------------------------------------------------------
# LEARNING CONTENT
# -------------------------------------------------------------
class LearningContent(Base):
    __tablename__ = 'learning_content'

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500))
    difficulty = Column(String(20))
    estimated_minutes = Column(Integer)
    topic = Column(String(100))
    module = Column(String(100))
    prerequisites = Column(String(200))
    url = Column(String(300))

# -------------------------------------------------------------
# STUDENT PROGRESS
# -------------------------------------------------------------
class StudentProgress(Base):
    __tablename__ = 'student_progress'

    id = Column(Integer, primary_key=True)
    id_student = Column(Integer, nullable=False)
    content_id = Column(Integer, nullable=False)

    status = Column(String(20))
    time_spent = Column(Integer)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

# -------------------------------------------------------------
# TASKS TABLE
# -------------------------------------------------------------
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(String(500))
    deadline = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")

    procrastination_risk = Column(Float, default=0.0)
    breakdown_generated = Column(Boolean, default=False)

    # Relationships
    student = relationship("Student", back_populates="tasks")
    subtasks = relationship("SubTask", back_populates="task", cascade="all, delete")
    events = relationship("TaskEvent", back_populates="task", cascade="all, delete")
    commitments = relationship("Commitment", back_populates="task")

# -------------------------------------------------------------
# SUBTASKS TABLE
# -------------------------------------------------------------
class SubTask(Base):
    __tablename__ = 'subtasks'

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    title = Column(String(200), nullable=False)
    order = Column(Integer)
    is_completed = Column(Boolean, default=False)

    task = relationship("Task", back_populates="subtasks")

# -------------------------------------------------------------
# TASK EVENTS TABLE
# -------------------------------------------------------------
class TaskEvent(Base):
    __tablename__ = "task_events"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    event_type = Column(String(50))
    timestamp = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="events")

# -------------------------------------------------------------
# COMMITMENTS
# -------------------------------------------------------------
class Commitment(Base):
    __tablename__ = 'commitments'

    id = Column(Integer, primary_key=True)
    id_student = Column(Integer, nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    commitment_type = Column(String(50))
    committed_datetime = Column(DateTime, nullable=False)
    pledge_text = Column(String(200))

    status = Column(String(20), default='pending')
    completed_at = Column(DateTime)
    points_at_stake = Column(Integer, default=10)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    task = relationship("Task", back_populates="commitments")

# -------------------------------------------------------------
# STUDENT POINTS
# -------------------------------------------------------------
class StudentPoints(Base):
    __tablename__ = 'student_points'

    id = Column(Integer, primary_key=True)
    id_student = Column(Integer, unique=True)

    total_points = Column(Integer, default=100)
    total_commitments = Column(Integer, default=0)
    kept_commitments = Column(Integer, default=0)
    broken_commitments = Column(Integer, default=0)
    points_earned = Column(Integer, default=0)
    points_lost = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)

    last_commitment_date = Column(DateTime)

# -------------------------------------------------------------
# ACCOUNTABILITY PARTNERS
# -------------------------------------------------------------
class AccountabilityPartner(Base):
    __tablename__ = 'accountability_partners'

    id = Column(Integer, primary_key=True)
    id_student = Column(Integer, nullable=False)

    partner_name = Column(String(100), nullable=False)
    partner_email = Column(String(150))
    partner_phone = Column(String(20))

    notify_on_deadline = Column(Boolean, default=True)
    notify_on_completion = Column(Boolean, default=True)
    notify_on_miss = Column(Boolean, default=True)
    send_weekly_digest = Column(Boolean, default=True)

    is_active = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)

# -------------------------------------------------------------
# MODEL PREDICTIONS
# -------------------------------------------------------------
class ModelPrediction(Base):
    __tablename__ = "model_predictions"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    model_version = Column(String(50), nullable=False)
    prediction = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    features_used = Column(String)

def log_prediction(user_id, prediction, confidence, features, model_version="rf_v1.2"):
    session = get_session()
    import json

    entry = ModelPrediction(
        user_id=user_id,
        model_version=model_version,
        prediction=prediction,
        confidence=confidence,
        features_used=json.dumps(features)
    )
    session.add(entry)
    session.commit()
    session.close()

# -------------------------------------------------------------
# NUDGE FEEDBACK
# -------------------------------------------------------------
class NudgeFeedback(Base):
    __tablename__ = "nudge_feedback"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    nudge_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    feedback = Column(String(50))
    outcome = Column(String(50))
    comments = Column(String(500))

def log_nudge_feedback(user_id, nudge_id, feedback, outcome, comments=""):
    session = get_session()
    entry = NudgeFeedback(
        user_id=user_id,
        nudge_id=nudge_id,
        feedback=feedback,
        outcome=outcome,
        comments=comments
    )
    session.add(entry)
    session.commit()
    session.close()

# -------------------------------------------------------------
# INIT DB FUNCTION
# -------------------------------------------------------------
def init_db(db_name='procrastination.db'):
    local_engine = get_engine(f"sqlite:///{db_name}")
    Base.metadata.create_all(local_engine)
    print(f"✅ Database created: {db_name}")
    return local_engine

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Database initialized.")
