"""Student Progress Tracking"""
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from database_setup import StudentProgress
from datetime import datetime

class ProgressTracker:
    def __init__(self):
        engine = create_engine('sqlite:///procrastination.db')
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def start_content(self, student_id, content_id):
        """Mark content as started"""
        progress = StudentProgress(
            id_student=student_id,
            content_id=content_id,
            status='in_progress',
            started_at=datetime.utcnow(),
            time_spent=0
        )
        self.session.add(progress)
        self.session.commit()
        return {'success': True, 'message': 'Content started'}
    
    def complete_content(self, student_id, content_id, time_spent):
        """Mark content as completed"""
        progress = self.session.query(StudentProgress).filter(
            and_(
                StudentProgress.id_student == student_id,
                StudentProgress.content_id == content_id
            )
        ).first()
        
        if progress:
            progress.status = 'completed'
            progress.completed_at = datetime.utcnow()
            progress.time_spent = time_spent
        else:
            progress = StudentProgress(
                id_student=student_id,
                content_id=content_id,
                status='completed',
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                time_spent=time_spent
            )
            self.session.add(progress)
        
        self.session.commit()
        return {'success': True, 'message': 'Content completed'}
    
    def get_stats(self, student_id):
        """Get student statistics"""
        all_progress = self.session.query(StudentProgress).filter(
            StudentProgress.id_student == student_id
        ).all()
        
        completed = [p for p in all_progress if p.status == 'completed']
        in_progress = [p for p in all_progress if p.status == 'in_progress']
        total_time = sum(p.time_spent or 0 for p in all_progress)
        
        return {
            'student_id': student_id,
            'completed': len(completed),
            'in_progress': len(in_progress),
            'total_time_minutes': total_time,
            'completion_rate': len(completed) / len(all_progress) * 100 if all_progress else 0
        }

# Test
if __name__ == "__main__":
    tracker = ProgressTracker()
    
    # Simulate student activity
    student_id = 11391
    
    # Start first content
    tracker.start_content(student_id, 1)
    print("✅ Started content 1")
    
    # Complete it
    tracker.complete_content(student_id, 1, time_spent=12)
    print("✅ Completed content 1 (12 min)")
    
    # Get stats
    stats = tracker.get_stats(student_id)
    print(f"\n📊 Stats:")
    print(f"  Completed: {stats['completed']}")
    print(f"  In Progress: {stats['in_progress']}")
    print(f"  Total Time: {stats['total_time_minutes']} min")