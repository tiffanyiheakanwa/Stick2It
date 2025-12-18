from sqlalchemy import (
    create_engine, Column, Integer, Float, String, Boolean,
    DateTime, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

engine = create_engine(
    "sqlite:///procrastination.db",
    connect_args={"check_same_thread": False}
)
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

    # Relationships
    tasks = relationship("Task", back_populates="student")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

# -------------------------------------------------------------
# STUDENT BEHAVIOR (For ML Features)
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
# DEPRECATED BUT KEPT FOR OPTION 2
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
# STUDENT PROGRESS (OPTIONAL, NOT USED IN TASK MODE)
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
# NEW: TASKS TABLE
# -------------------------------------------------------------
class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("students.id"), nullable=False)

    title = Column(String(200), nullable=False)
    description = Column(String(500))
    deadline = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default="pending")  # pending, in_progress, completed, overdue

    procrastination_risk = Column(Float, default=0.0)
    breakdown_generated = Column(Boolean, default=False)

    # Relationships
    student = relationship("Student", back_populates="tasks")
    subtasks = relationship("SubTask", back_populates="task", cascade="all, delete")
    events = relationship("TaskEvent", back_populates="task", cascade="all, delete")
    commitments = relationship("Commitment", back_populates="task")

# -------------------------------------------------------------
# NEW: SUBTASKS TABLE
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
# NEW: TASK EVENTS TABLE (NUDGES, DEADLINES, ETC.)
# -------------------------------------------------------------
class TaskEvent(Base):
    __tablename__ = "task_events"

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)

    event_type = Column(String(50))  # "nudge_sent", "deadline", etc.
    timestamp = Column(DateTime, default=datetime.utcnow)

    task = relationship("Task", back_populates="events")

# -------------------------------------------------------------
# COMMITMENTS (UPDATED TO LINK TO TASK INSTEAD OF CONTENT)
# -------------------------------------------------------------
class Commitment(Base):
    __tablename__ = 'commitments'

    id = Column(Integer, primary_key=True)
    id_student = Column(Integer, nullable=False)

    # This replaces content_id
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)

    commitment_type = Column(String(50))
    committed_datetime = Column(DateTime, nullable=False)
    pledge_text = Column(String(200))

    status = Column(String(20), default='pending')
    completed_at = Column(DateTime)

    points_at_stake = Column(Integer, default=10)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    task = relationship("Task", back_populates="commitments")

# -------------------------------------------------------------
# STUDENT POINT SYSTEM
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
# INIT DB
# -------------------------------------------------------------
def init_db(db_name='procrastination.db'):
    local_engine = create_engine(f'sqlite:///{db_name}')
    Base.metadata.create_all(local_engine)
    print(f"✅ Database created: {db_name}")
    return local_engine

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Database initialized.")
