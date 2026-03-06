from backend.app.database import get_db_session
from backend.app.models import Commitment, Assignment, Student
from datetime import datetime, timedelta
import uuid

with get_db_session() as session:
    # 1. Ensure a test student exists
    student = session.query(Student).first()
    if not student:
        student = Student(name="Test Student", email="test@cu.edu.ng", password_hash="hash")
        session.add(student)
        session.flush()

    # 2. Ensure a test assignment exists
    assignment = session.query(Assignment).first()
    if not assignment:
        assignment = Assignment(
            title="CSC 411 Quiz", 
            due_date=datetime.utcnow() + timedelta(days=2),
            student_id=student.id
        )
        session.add(assignment)
        session.flush()

    # 3. Create the Commitment
    test_token = str(uuid.uuid4())
    new_commit = Commitment(
        student_id=student.id,
        assignment_id=assignment.id,
        stake_type="Points",
        stake_value=50,
        penalty_message="I will treat the class to lunch if I fail.",
        buddy_name="Accountability Buddy",
        buddy_email="buddy@example.com",
        verification_token=test_token,
        status="pending"
    )
    
    session.add(new_commit)
    session.commit()
    print(f"✅ Created commitment with token: {test_token}")