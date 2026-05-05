from backend.app.database import get_db_session
from backend.app.models import Student

with get_db_session() as session:
    student = session.query(Student).get(1)
    print(f"Student 1 FCM Token: {student.fcm_token}")
    print(f"Student 1 Email: {student.email}")
