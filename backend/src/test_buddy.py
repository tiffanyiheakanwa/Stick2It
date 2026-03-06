from backend.app.database import get_db_session
from backend.app.models import Commitment, Assignment
from datetime import datetime, timedelta
import uuid

with get_db_session() as session:
    # 1. Ensure at least one assignment exists
    assignment = session.query(Assignment).first()
    if not assignment:
        assignment = Assignment(title="Test Task", due_date=datetime.utcnow() + timedelta(days=1))
        session.add(assignment)
        session.flush()

    # 2. Create a test commitment with a unique token
    test_token = str(uuid.uuid4())
    new_commit = Commitment(
        student_id=1, # Ensure this matches a student ID in your DB
        assignment_id=assignment.id,
        buddy_name="Test Buddy",
        buddy_email="buddy@example.com",
        verification_token=test_token,
        stake_type="Points",
        stake_value=50,
        penalty_message="Post an embarrassing photo",
        status="pending"
    )
    session.add(new_commit)
    session.commit()
    print(f"✅ Test Token Created: {test_token}")
    print(f"🔗 Test URL: http://localhost:8000/verify/{test_token}")