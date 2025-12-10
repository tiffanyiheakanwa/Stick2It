from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean
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

def init_db(db_name='procrastination.db'):
    local_engine = create_engine(f'sqlite:///{db_name}')
    Base.metadata.create_all(local_engine)
    print(f"✅ Database created: {db_name}")
    return local_engine

if __name__ == "__main__":
    Base.metadata.create_all(engine)
    print("Database initialized.")