# setup_test_db.py
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime, timedelta
from database_setup import Base, engine, SessionLocal, Student, StudentBehavior, StudentPoints

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def seed_test_student():
    session = SessionLocal()

    # Check if the test student already exists
    existing = session.query(Student).filter_by(id_student=9999).first()
    if existing:
        print("⚠️ Test student already exists, skipping creation.")
        session.close()
        return

    # Create a test student
    test_student = Student(
        id_student=9999,
        name="Test Student",
        email="test@student.com",
        password_hash="hashed_password",
        created_at=datetime.utcnow(),
        is_active=True,
        model_opt_out=False,
        no_nudges=False,
    )
    session.add(test_student)
    session.commit()

    # Optional: add behavior
    behavior = StudentBehavior(
        id_student=test_student.id,
        last_minute_ratio=0.75,
        engagement_intensity=10.5,
        deadline_pressure=3.2,
        login_consistency=0.8,
        early_starter=0,
        completion_rate=0.4,
        activity_span=20.0
    )
    session.add(behavior)

    # Optional: add points
    points = StudentPoints(
        id_student=test_student.id,
        total_points=50,
        current_streak=3,
        last_commitment_date=datetime.utcnow() - timedelta(days=1)
    )
    session.add(points)

    session.commit()
    session.close()
    print("✅ Test student and related data seeded successfully!")

if __name__ == "__main__":
    create_tables()
    seed_test_student()
