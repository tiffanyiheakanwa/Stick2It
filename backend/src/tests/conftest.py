import sys
import os
import pytest
from sqlalchemy.orm import sessionmaker

# Ensure backend root is in the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Configure test database URL before importing database module
os.environ["DATABASE_URL"] = "sqlite:///test_procrastination.db"

from backend.app.database import engine, Base, SessionLocal

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # Recreate all tables using the app models Base
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)
    try:
        if os.path.exists("test_procrastination.db"):
            os.remove("test_procrastination.db")
    except Exception:
        pass

@pytest.fixture(scope="function")
def session():
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()
