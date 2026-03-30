"""Adaptive Learning Recommendation Engine"""
from backend.app.database import get_db_session
from backend.app.models import LearningContent, StudentProgress
from .predict import ProcrastinationPredictor

class AdaptiveRecommender:
    def __init__(self):
        self.predictor = ProcrastinationPredictor()

    def get_completed_content(self, session, student_id):
        """Get IDs of completed content"""
        completed = session.query(StudentProgress).filter(
            StudentProgress.student_id == student_id,
            StudentProgress.status == 'completed'
        ).all()
        return [p.content_id for p in completed]
    
    def get_available_content(self, session, completed_ids):
        """Get content where prerequisites are met"""
        all_content = session.query(LearningContent).all()
        available = []
        
        for content in all_content:
            if content.id in completed_ids:
                continue
            
            if content.prerequisites:
                prereq_ids = [int(x) for x in content.prerequisites.split(',')]
                if all(pid in completed_ids for pid in prereq_ids):
                    available.append(content)
            else:
                available.append(content)
        
        return available
    
    def recommend(self, student_id, limit=5):
        """Generate personalized recommendations"""
        
        # Get risk prediction
        try:
            pred = self.predictor.predict_from_database(student_id)
            risk = pred.get('risk_category', 'medium').lower()
            score = float(pred.get('risk_score', 50.0))
        except Exception:
            risk = 'medium'
            score = 50.0
        
        # Get available content
        # Get available content
        with get_db_session() as session:
            completed = self.get_completed_content(session, student_id)
            available = self.get_available_content(session, completed)
        
            # Recommend based on risk level
            if risk == 'high':
                recommendations = self._recommend_high_risk(available, limit)
                strategy = "Start with shorter, easier tasks to build momentum"
            elif risk == 'low':
                recommendations = self._recommend_low_risk(available, limit)
                strategy = "Challenge yourself with advanced content"
            else:
                recommendations = self._recommend_medium_risk(available, limit)
                strategy = "Balanced progression through material"
            
            return {
                'student_id': student_id,
                'risk_level': risk,
                'risk_score': score,
                'strategy': strategy,
                'completed': len(completed),
                'recommendations': [{
                    'id': c.id,
                    'title': c.title,
                    'difficulty': c.difficulty,
                    'minutes': c.estimated_minutes,
                    'topic': c.topic,
                    'module': c.module,
                    'url': c.url
                } for c in recommendations]
            }
    
    def _recommend_high_risk(self, available, limit):
        """For high-risk: easy, short tasks"""
        # Study skills first
        study = [c for c in available if c.topic == 'Study Skills'][:2]
        
        # Then easy content, shortest first
        easy = [c for c in available if c.difficulty == 'easy' and c not in study]
        easy.sort(key=lambda x: x.estimated_minutes)
        
        result = study + easy
        return result[:limit]
    
    def _recommend_medium_risk(self, available, limit):
        """For medium-risk: balanced mix"""
        easy = [c for c in available if c.difficulty == 'easy'][:2]
        medium = [c for c in available if c.difficulty == 'medium'][:3]
        return (easy + medium)[:limit]
    
    def _recommend_low_risk(self, available, limit):
        """For low-risk: challenging content"""
        hard = [c for c in available if c.difficulty == 'hard'][:3]
        medium = [c for c in available if c.difficulty == 'medium'][:2]
        return (hard + medium)[:limit]

# Test it
if __name__ == "__main__":
    rec = AdaptiveRecommender()
    result = rec.recommend(11391, limit=5)
    
    print(f"\n🎯 Student {result['student_id']}")
    print(f"Risk: {result['risk_level'].upper()} ({result['risk_score']:.1f}%)")
    print(f"Strategy: {result['strategy']}")
    print(f"\n📚 Top {len(result['recommendations'])} Recommendations:\n")
    
    for i, item in enumerate(result['recommendations'], 1):
        print(f"{i}. {item['title']}")
        print(f"   {item['difficulty']} | {item['minutes']} min | {item['module']}")
        print()