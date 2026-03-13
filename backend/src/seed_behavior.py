from backend.app.database import get_db_session
from backend.app.models import StudentBehavior

with get_db_session() as session:
    # Tiffany's record
    tiffany_behavior = StudentBehavior(
        student_id=2,
        last_minute_ratio=0.15,      # Low procrastination
        completion_rate=0.85,        # High completion
        engagement_intensity=12.0,
        deadline_pressure=1.2,
        login_consistency=0.9,
        early_starter=1,
        activity_span=14.0
    )
    session.add(tiffany_behavior)
    session.commit()
    print("✅ Behavior profile created for Student 2!")