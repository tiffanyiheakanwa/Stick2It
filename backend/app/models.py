from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from .database import Base 

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(120), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    avg_success_rate = Column(Float, default=0.0) 
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Password helpers migrated from database_setup_content.py
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Relationships
    assignments = relationship("Assignment", back_populates="student")
    points = relationship("StudentPoints", uselist=False, back_populates="student")
    behavior = relationship("StudentBehavior", uselist=False, back_populates="student")

class StudentBehavior(Base):
    """ Migrated for AI Feature Set Support """
    __tablename__ = 'behaviors'
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
    student_id = Column(Integer, ForeignKey("students.id"))
    title = Column(String(200))
    description = Column(Text)
    due_date = Column(DateTime)
    status = Column(String(20), default="Pending") 
    
    student = relationship("Student", back_populates="assignments")
    commitment = relationship("Commitment", back_populates="assignment", uselist=False)

class Commitment(Base):
    """ High-Stakes Social Penalties with Buddy Verification """
    __tablename__ = 'commitments'
    id = Column(Integer, primary_key=True)
    assignment_id = Column(Integer, ForeignKey("assignments.id"))
    student_id = Column(Integer, ForeignKey("students.id")) # Explicit link for easy queries
    
    stake_type = Column(String(50)) # 'Financial', 'Social', 'Points'
    stake_value = Column(Integer, default=10)
    penalty_message = Column(Text) 
    
    buddy_name = Column(String(100))
    buddy_email = Column(String(150))
    is_verified_by_buddy = Column(Boolean, default=False)
    verification_token = Column(String(100), unique=True) 
    
    status = Column(String(20), default='pending') 
    created_at = Column(DateTime, default=func.now())
    assignment = relationship("Assignment", back_populates="commitment")

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

class Nudge(Base):
    __tablename__ = "nudges"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    assignment_id = Column(Integer, ForeignKey("assignments.id"), nullable=True)
    message = Column(Text)
    nudge_type = Column(String(50)) 
    sent_at = Column(DateTime(timezone=True), server_default=func.now())