from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

engine = create_engine("sqlite:///procrastination.db", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    return SessionLocal()

class Student(Base):
    __tablename__ = 'students'
    
    id = Column(Integer, primary_key=True)
    id_student = Column(Integer, unique=True)
    final_result = Column(String(20))

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

def init_db(db_name='procrastination.db'):
    local_engine = create_engine(f'sqlite:///{db_name}')
    Base.metadata.create_all(local_engine)
    print(f"✅ Database created: {db_name}")
    return local_engine

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Database initialized.")