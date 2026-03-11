from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.models import LearningContent

engine = create_engine('sqlite:///procrastination.db')
Session = sessionmaker(bind=engine)
session = Session()


# Add 16 sample learning items
content = [
    # Easy items (for high-risk students)
    {'title': 'Welcome & Overview', 'description': 'Course introduction', 
     'difficulty': 'easy', 'estimated_minutes': 10, 'topic': 'Intro', 
     'module': 'Module 1', 'prerequisites': '', 'url': 'https://example.com/1'},
    
    {'title': 'Study Skills Guide', 'description': 'Effective learning techniques', 
     'difficulty': 'easy', 'estimated_minutes': 15, 'topic': 'Study Skills', 
     'module': 'Bonus', 'prerequisites': '', 'url': 'https://example.com/2'},
    
    {'title': 'Time Management Tips', 'description': 'Managing your schedule', 
     'difficulty': 'easy', 'estimated_minutes': 20, 'topic': 'Study Skills', 
     'module': 'Bonus', 'prerequisites': '', 'url': 'https://example.com/3'},
    
    {'title': 'Basic Concepts Quiz', 'description': 'Test fundamentals', 
     'difficulty': 'easy', 'estimated_minutes': 15, 'topic': 'Assessment', 
     'module': 'Module 1', 'prerequisites': '1', 'url': 'https://example.com/4'},
    
    {'title': 'Setup Tutorial', 'description': 'Environment setup guide', 
     'difficulty': 'easy', 'estimated_minutes': 25, 'topic': 'Setup', 
     'module': 'Module 1', 'prerequisites': '1', 'url': 'https://example.com/5'},
    
    # Medium items (for medium-risk students)
    {'title': 'Data Structures', 'description': 'Arrays and lists', 
     'difficulty': 'medium', 'estimated_minutes': 30, 'topic': 'Programming', 
     'module': 'Module 2', 'prerequisites': '4,5', 'url': 'https://example.com/6'},
    
    {'title': 'Algorithm Basics', 'description': 'Sorting and searching', 
     'difficulty': 'medium', 'estimated_minutes': 35, 'topic': 'Algorithms', 
     'module': 'Module 2', 'prerequisites': '6', 'url': 'https://example.com/7'},
    
    {'title': 'Practice Problems', 'description': 'Coding exercises', 
     'difficulty': 'medium', 'estimated_minutes': 45, 'topic': 'Practice', 
     'module': 'Module 2', 'prerequisites': '6,7', 'url': 'https://example.com/8'},
    
    {'title': 'Mid-Course Assessment', 'description': 'Comprehensive quiz', 
     'difficulty': 'medium', 'estimated_minutes': 40, 'topic': 'Assessment', 
     'module': 'Module 2', 'prerequisites': '8', 'url': 'https://example.com/9'},
    
    {'title': 'Code Review Workshop', 'description': 'Review best practices', 
     'difficulty': 'medium', 'estimated_minutes': 30, 'topic': 'Best Practices', 
     'module': 'Module 3', 'prerequisites': '9', 'url': 'https://example.com/10'},
    
    # Hard items (for low-risk students)
    {'title': 'Advanced Data Structures', 'description': 'Trees and graphs', 
     'difficulty': 'hard', 'estimated_minutes': 50, 'topic': 'Advanced', 
     'module': 'Module 3', 'prerequisites': '9', 'url': 'https://example.com/11'},
    
    {'title': 'Dynamic Programming', 'description': 'Complex algorithms', 
     'difficulty': 'hard', 'estimated_minutes': 60, 'topic': 'Algorithms', 
     'module': 'Module 3', 'prerequisites': '11', 'url': 'https://example.com/12'},
    
    {'title': 'System Design', 'description': 'Architecture principles', 
     'difficulty': 'hard', 'estimated_minutes': 70, 'topic': 'Design', 
     'module': 'Module 4', 'prerequisites': '11,12', 'url': 'https://example.com/13'},
    
    {'title': 'Capstone Project', 'description': 'Final comprehensive project', 
     'difficulty': 'hard', 'estimated_minutes': 120, 'topic': 'Project', 
     'module': 'Module 4', 'prerequisites': '13', 'url': 'https://example.com/14'},
    
    {'title': 'Interview Prep', 'description': 'Technical interview practice', 
     'difficulty': 'hard', 'estimated_minutes': 90, 'topic': 'Career', 
     'module': 'Module 4', 'prerequisites': '12', 'url': 'https://example.com/15'},
    
    {'title': 'Portfolio Development', 'description': 'Build your portfolio', 
     'difficulty': 'hard', 'estimated_minutes': 80, 'topic': 'Career', 
     'module': 'Module 4', 'prerequisites': '14', 'url': 'https://example.com/16'},
]

for item in content:
    session.add(LearningContent(**item))

session.commit()
print(f"✅ Added {len(content)} learning items")

# Show summary
for diff in ['easy', 'medium', 'hard']:
    count = session.query(LearningContent).filter(
        LearningContent.difficulty == diff
    ).count()
    print(f"  {diff.capitalize()}: {count} items")

session.close()