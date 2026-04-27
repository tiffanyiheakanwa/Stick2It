import sys
sys.path.append('.')
from backend.app.database import get_db_session
from backend.app.models import Prediction

with get_db_session() as session:
    preds = session.query(Prediction).all()
    for p in preds:
        print(f"ID: {p.id}, score: {p.risk_score}")
