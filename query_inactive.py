from backend.app.database import get_db_session
from backend.app.models import StudentBehavior
from datetime import datetime, timezone

now = datetime.now(timezone.utc).replace(tzinfo=None)

with get_db_session() as session:
    b = session.query(StudentBehavior).filter_by(student_id=1).first()
    if b and b.last_login:
        last_login = b.last_login.replace(tzinfo=None) if b.last_login.tzinfo else b.last_login
        days_inactive = (now - last_login).days
        print(f"Days inactive: {days_inactive}")
    else:
        print("No behavior or last_login")
