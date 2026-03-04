from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# Import the Base and models from your app's central location
from .models import Base 

# Configured for SQLite with thread safety for multi-threaded apps
DB_URL = "sqlite:///procrastination.db"
engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_session():
    """ Provides a database session for backend operations """
    return SessionLocal()

def init_db():
    """ 
    Initializes the database schema. 
    Use this during setup to create all tables defined in models.py.
    """
    Base.metadata.create_all(bind=engine)
    print(f"✅ Database initialized: {DB_URL}")

if __name__ == "__main__":
    init_db()