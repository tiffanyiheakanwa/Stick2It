"""Student Progress Tracking (Integrity-Enforced)"""

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from backend.app.models import StudentProgress
from datetime import datetime
from .logger import logger
from .utils import safe_execute

class ProgressTracker:
    def __init__(self):
        engine = create_engine("sqlite:///procrastination.db")
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def start_content(self, student_id, content_id):
        """Mark content as started (only once)"""

        existing = self.session.query(StudentProgress).filter(
            and_(
                StudentProgress.id_student == student_id,
                StudentProgress.content_id == content_id
            )
        ).first()

        if existing:
            return {
                "success": False,
                "message": "Content already started"
            }

        progress = StudentProgress(
            id_student=student_id,
            content_id=content_id,
            status="in_progress",
            started_at=datetime.utcnow(),
            time_spent=0
        )

        self.session.add(progress)
        self.session.commit()

        return {"success": True, "message": "Content started"}

    def complete_content(self, student_id, content_id, time_spent):
        """Mark content as completed (bounded & safe)"""
        logger.info(f"Student {student_id} completing content {content_id} with time spent {time_spent} minutes")
        time_spent = max(0, time_spent)

        progress = self.session.query(StudentProgress).filter(
            and_(
                StudentProgress.id_student == student_id,
                StudentProgress.content_id == content_id
            )
        ).first()

        if progress and progress.status == "completed":
            return {
                "success": True,
                "message": "Content already completed"
            }

        if not progress:
            progress = StudentProgress(
                id_student=student_id,
                content_id=content_id,
                status="completed",
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                time_spent=time_spent
            )
            self.session.add(progress)
        else:
            progress.status = "completed"
            progress.completed_at = datetime.utcnow()
            progress.time_spent = time_spent

        self.session.commit()

        return {"success": True, "message": "Content completed"}

    def get_stats(self, student_id):
        """Get bounded student statistics"""

        all_progress = self.session.query(StudentProgress).filter(
            StudentProgress.id_student == student_id
        ).all()

        completed = [p for p in all_progress if p.status == "completed"]
        in_progress = [p for p in all_progress if p.status == "in_progress"]

        total_time = sum(max(0, p.time_spent or 0) for p in all_progress)

        completion_rate = (
            len(completed) / len(all_progress) * 100
            if all_progress else 0
        )

        completion_rate = min(100, round(completion_rate, 2))

        return {
            "student_id": student_id,
            "completed": len(completed),
            "in_progress": len(in_progress),
            "total_time_minutes": total_time,
            "completion_rate": completion_rate
        }

    def close(self):
        self.session.close()
