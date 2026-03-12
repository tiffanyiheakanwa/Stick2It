from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .database import Base 

partnerships = Table(
    'partnerships',
    Base.metadata,
    Column('student_id', Integer, ForeignKey('students.id'), primary_key=True),
    Column('partner_id', Integer, ForeignKey('students.id'), primary_key=True)
)

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(120), unique=True, index=True, nullable=False)
    avg_success_rate = Column(Float, default=0.5) 
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    no_nudges = Column(Boolean, default=False)      # Opt-out for nudges
    model_opt_out = Column(Boolean, default=False)  # Opt-out for ML modeling

    partners = relationship(
        "Student",
        secondary=partnerships,
        primaryjoin=(id == partnerships.c.student_id),
        secondaryjoin=(id == partnerships.c.partner_id),
        backref="added_by"
    )
    
    # Password helpers migrated from database_setup_content.py
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Relationships
    assignments = relationship("Assignment", back_populates="student")
    commitments = relationship("Commitment", back_populates="student")
    points = relationship("StudentPoints", back_populates="student", uselist=False)
    behavior = relationship("StudentBehavior", back_populates="student", uselist=False)
    nudges = relationship("Nudge", back_populates="student")
    predictions = relationship("Prediction", back_populates="student")

class StudentBehavior(Base):
    """ Migrated for AI Feature Set Support """
    __tablename__ = 'student_behavior'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    last_minute_ratio = Column(Float)
    engagement_intensity = Column(Float)
    deadline_pressure = Column(Float)
    login_consistency = Column(Float)
    early_starter = Column(Integer)
    completion_rate = Column(Float)
    activity_span = Column(Float)
    high_risk = Column(Boolean)
    
    student = relationship("Student", back_populates="behavior")

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    due_date = Column(DateTime)
    status = Column(String(20), default="Pending") 
    student_id = Column(Integer, ForeignKey("students.id"))
    
    student = relationship("Student", back_populates="assignments")
    commitments = relationship("Commitment", back_populates="assignment", uselist=False)

class Commitment(Base):
    """ High-Stakes Social Penalties with Buddy Verification """
    __tablename__ = 'commitments'
    id = Column(Integer, primary_key=True, index= True)
    student_id = Column(Integer, ForeignKey("students.id")) # Explicit link for easy queries
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    content_id = Column(Integer, ForeignKey("learning_content.id"), nullable=True) # Linked to adaptive content
    custom_title = Column(String(200), nullable=True)

    stake_type = Column(String(50)) # 'Financial', 'Social', 'Points'
    stake_value = Column(Integer, default=10)
    penalty_message = Column(Text) 
    
    buddy_name = Column(String(100))
    buddy_email = Column(String(150))
    is_verified_by_buddy = Column(Boolean, default=False)
    verification_token = Column(String(100), unique=True) 
    
    status = Column(String(20), default='pending') 
    created_at = Column(DateTime, default=func.now())
    committed_datetime = Column(DateTime)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    student = relationship("Student", back_populates="commitments")
    assignment = relationship("Assignment", back_populates="commitments")

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=True)
    action_type = Column(String(50)) 
    nudge_id = Column(Integer, ForeignKey("nudges.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class StudentPoints(Base):
    __tablename__ = 'student_points'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), unique=True)
    total_points = Column(Integer, default=100)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    last_commitment_date = Column(DateTime)
    
    student = relationship("Student", back_populates="points")

class LearningContent(Base):
    """Data for the Adaptive Recommender"""
    __tablename__ = "learning_content"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    difficulty = Column(String)  # easy, medium, hard
    estimated_minutes = Column(Integer)
    topic = Column(String)
    module = Column(String)
    url = Column(String)
    prerequisites = Column(String)  # Comma-separated IDs

class StudentProgress(Base):
    __tablename__ = "student_progress"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    content_id = Column(Integer, ForeignKey("learning_content.id"))
    status = Column(String)  # started, completed
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class Nudge(Base):
    __tablename__ = "nudges"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=True)
    message = Column(Text)
    nudge_type = Column(String(50)) 
    sent_at = Column(DateTime(timezone=True), server_default=func.now())

    student = relationship("Student", back_populates="nudges")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("students.id"))
    sender_id = Column(Integer, ForeignKey("students.id"))
    message = Column(Text)
    type = Column(String(50)) # e.g., 'buddy_request', 'system_alert'
    status = Column(String(20), default="unread") # unread, read, accepted, declined
    created_at = Column(DateTime, server_default=func.now())

    recipient = relationship("Student", foreign_keys=[recipient_id])
    sender = relationship("Student", foreign_keys=[sender_id])
    
class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    risk_score = Column(Float)
    reason = Column(String(255))
    predicted_at = Column(DateTime, server_default=func.now())

    student = relationship("Student", back_populates="predictions")