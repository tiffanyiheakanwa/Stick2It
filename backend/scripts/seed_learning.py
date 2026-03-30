from backend.app.database import get_db_session
from backend.app.models import LearningContent

def seed():
    with get_db_session() as session:
        if session.query(LearningContent).count() == 0:
            print("Seeding LearningContent...")
            items = [
                {"title": "Pomodoro Technique Basics", "difficulty": "easy", "estimated_minutes": 10, "topic": "Study Skills", "module": "Time Management", "url": "https://example.com/pomodoro"},
                {"title": "Breaking Down Large Tasks", "difficulty": "easy", "estimated_minutes": 15, "topic": "Goal Setting", "module": "Planning", "url": "https://example.com/breakdown"},
                {"title": "Overcoming Perfectionism", "difficulty": "medium", "estimated_minutes": 20, "topic": "Mindset", "module": "Psychology", "url": "https://example.com/perfectionism"},
                {"title": "Deep Work Fundamentals", "difficulty": "hard", "estimated_minutes": 30, "topic": "Focus", "module": "Productivity", "url": "https://example.com/deepwork"},
                {"title": "Managing Deadline Anxiety", "difficulty": "medium", "estimated_minutes": 20, "topic": "Study Skills", "module": "Psychology", "url": "https://example.com/anxiety"},
            ]
            for item in items:
                session.add(LearningContent(**item))
            session.commit()
            print("LearningContent seeded successfully.")
        else:
            print("LearningContent already seeded.")

if __name__ == "__main__":
    seed()
