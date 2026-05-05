from backend.app.database import get_db_session
from backend.app.models import Commitment
from datetime import datetime, timezone

now = datetime.now(timezone.utc).replace(tzinfo=None)

with get_db_session() as session:
    c = session.query(Commitment).get(7)
    target_date = c.assignment.due_date if c.assignment else c.committed_datetime
    
    print(f"Commitment 7:")
    print(f"Target Date: {target_date}")
    print(f"Now: {now}")
    
    if target_date:
        hours_left = (target_date - now).total_seconds() / 3600
        print(f"Hours left: {hours_left}")
        print(f"Int Hours left: {int(hours_left)}")
