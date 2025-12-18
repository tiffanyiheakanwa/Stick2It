from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()

engine = create_engine("sqlite:///procrastination.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()


class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    
    id_student = Column(Integer, unique=True)
    
    # Add these for authentication
    name = Column(String(100))
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    # Optional field already in model
    final_result = Column(String(20))

    # Password helpers
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

class StudentBehavior(Base):
    __tablename__ = 'behaviors'
    
    id = Column(Integer, primary_key=True)
    id_student = Column(Integer)
    
    # 7 features
    last_minute_ratio = Column(Float)
    engagement_intensity = Column(Float)
    deadline_pressure = Column(Float)
    login_consistency = Column(Float)
    early_starter = Column(Integer)
    completion_rate = Column(Float)
    activity_span = Column(Float)
    
    # Target
    high_risk = Column(Boolean)
    
    # Raw metrics
    num_login_days = Column(Integer)
    total_clicks = Column(Integer)
    avg_score = Column(Float)

class LearningContent(Base):
    __tablename__ = 'learning_content'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(String(500))
    difficulty = Column(String(20))     # easy, medium, hard
    estimated_minutes = Column(Integer)
    topic = Column(String(100))
    module = Column(String(100))
    prerequisites = Column(String(200)) # Comma-separated IDs
    url = Column(String(300))

class StudentProgress(Base):
    __tablename__ = 'student_progress'
    
    id = Column(Integer, primary_key=True)
    id_student = Column(Integer, nullable=False)
    content_id = Column(Integer, nullable=False)
    status = Column(String(20))         # not_started, in_progress, completed
    time_spent = Column(Integer)        # Minutes
    started_at = Column(DateTime)
    completed_at = Column(DateTime)

class Commitment(Base):
    __tablename__ = 'commitments'
    
    id = Column(Integer, primary_key=True)
    id_student = Column(Integer, nullable=False)
    content_id = Column(Integer, nullable=False)
    
    # The pledge
    commitment_type = Column(String(50))        # "start_time", "completion_deadline"
    committed_datetime = Column(DateTime, nullable=False)  # When they said they'd do it
    pledge_text = Column(String(200))           # "I will start Time Management by tomorrow 2pm"
    
    # Tracking
    status = Column(String(20), default='pending')  # pending, kept, broken, expired
    completed_at = Column(DateTime)
    
    # Points system
    points_at_stake = Column(Integer, default=10)   # Points they'll lose if they break it
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class StudentPoints(Base):
    __tablename__ = 'student_points'

    id = Column(Integer, primary_key=True)
    id_student = Column(Integer, unique=True)

    total_points = Column(Integer, default=100)      # start at 100?
    total_commitments = Column(Integer, default=0)
    kept_commitments = Column(Integer, default=0)
    broken_commitments = Column(Integer, default=0)
    points_earned = Column(Integer, default=0)
    points_lost = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)

    last_commitment_date = Column(DateTime)

class AccountabilityPartner(Base):
    __tablename__ = 'accountability_partners'
    
    id = Column(Integer, primary_key=True)
    id_student = Column(Integer, nullable=False)
    
    # Partner info (NOT in your system - external person)
    partner_name = Column(String(100), nullable=False)
    partner_email = Column(String(150))
    partner_phone = Column(String(20))
    
    # Notification preferences
    notify_on_deadline = Column(Boolean, default=True)      # Alert when deadline approaching
    notify_on_completion = Column(Boolean, default=True)    # Alert when task completed
    notify_on_miss = Column(Boolean, default=True)          # Alert when commitment broken
    send_weekly_digest = Column(Boolean, default=True)      # Weekly summary
    
    # Status
    is_active = Column(Boolean, default=True)
    verified = Column(Boolean, default=False)    # Did partner confirm via email?
    
    created_at = Column(DateTime, default=datetime.utcnow)    

def init_db(db_name='procrastination.db'):
    local_engine = create_engine(f'sqlite:///{db_name}')
    Base.metadata.create_all(local_engine)
    print(f"✅ Database created: {db_name}")
    return local_engine

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Database initialized.")