import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from sqlalchemy.orm import sessionmaker
from database_setup import Base, get_engine

# TEST_DATABASE_URL = "sqlite:///./test_procrastination.db"

@pytest.fixture(scope="session")
def engine():
    # engine = get_engine(TEST_DATABASE_URL)
    engine = get_engine("sqlite:///:memory:", echo=False)  
    Base.metadata.create_all(engine)  # ✅ CREATE TABLES
    yield engine
    Base.metadata.drop_all(engine)    # optional cleanup

@pytest.fixture(scope="function")
def session(engine):
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()
