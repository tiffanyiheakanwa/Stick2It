from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    title = Column(String)
    due_date = Column(DateTime)
    status = Column(String)

class Interaction(Base):
    __tablename__ = "interactions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)
    assignment_id = Column(Integer)
    action_type = Column(String)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)
    assignment_id = Column(Integer)
    risk_level = Column(String)
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())

class Nudge(Base):
    __tablename__ = "nudges"
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer)
    message = Column(String)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
