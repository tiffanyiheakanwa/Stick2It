"""
Smart Nudging System - Just-in-Time Adaptive Interventions
Based on: Nahum-Shani et al. (2018), Plak et al. (2023), Brandt et al. (2024)
"""
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker
from database_setup_content import (StudentProgress, Commitment, StudentPoints, 
                            LearningContent, StudentBehavior, AccountabilityPartner)
from datetime import datetime, timedelta
import random

class SmartNudgeSystem:
    def __init__(self):
        engine = create_engine('sqlite:///procrastination.db')
        Session = sessionmaker(bind=engine)
        self.session = Session()
        
        # Nudge templates based on research
        self.nudge_templates = {
            'inactivity': [
                "🎯 Hey {name}! You haven't logged in for {days} days. Your streak is waiting!",
                "⏰ Quick check-in: Just 15 minutes today can keep your {streak}-day streak alive!",
                "💪 Small steps matter! Even 10 minutes of study today counts."
            ],
            'deadline_approaching': [
                "⚠️ Deadline alert: '{content}' is due in {hours} hours. Start now?",
                "🚨 Only {hours}h left for '{content}'. Break it into smaller steps!",
                "⏳ Running low on time for '{content}'. Need help breaking it down?"
            ],
            'missed_commitment': [
                "😔 You missed your pledge for '{content}'. Want to reschedule?",
                "💭 Life happens! Recommit to '{content}' with a new time?",
                "🔄 Reset and try again? Set a new commitment for '{content}'."
            ],
            'success_reinforcement': [
                "🎉 Amazing! You kept your commitment! You're on a {streak}-day streak!",
                "⭐ Success! +{points} points earned. Keep this momentum going!",
                "🔥 {streak} days strong! You're building great habits!"
            ],
            'social_proof': [
                "👥 {percent}% of students in your cohort have completed '{content}'",
                "🏆 Top students spent an average of {minutes} min on this topic",
                "📊 Students who completed this early scored {points}% higher"
            ],
            'loss_aversion': [
                "⚠️ You're about to lose your {streak}-day streak! Quick 10-min session?",
                "💎 {points} points at risk! Complete your commitment to keep them.",
                "📉 Missing this will lower your overall performance—stay on track!"
            ],
            'progress_celebration': [
                "🎊 Milestone reached! {completed}/{total} items completed!",
                "📈 You're {percent}% through the course. Amazing progress!",
                "💯 Perfect completion rate this week! Keep it up!"
            ],
            'peer_encouragement': [
                "🤝 Your study buddy completed '{content}'. You're next!",
                "👊 {partner} is cheering for you! Show them what you've got!",
                "💪 Your accountability partner believes in you. Time to shine!"
            ]
        }
    
    def check_and_send_nudges(self, student_id):
        """
        Main function: Check student state and send appropriate nudges
        Returns list of nudges that should be sent
        """
        nudges = []
        
        # Get student data
        behavior = self._get_student_behavior(student_id)
        if not behavior:
            return nudges
        
        # Run all nudge checks
        nudges.extend(self._check_inactivity(student_id, behavior))
        nudges.extend(self._check_deadlines(student_id))
        nudges.extend(self._check_missed_commitments(student_id))
        nudges.extend(self._check_streak_risk(student_id))
        nudges.extend(self._check_progress_milestones(student_id))
        
        # Prioritize nudges (max 2 per day to avoid fatigue)
        nudges = self._prioritize_nudges(nudges)[:2]
        
        return nudges
    
    def _check_inactivity(self, student_id, behavior):
        """Check if student has been inactive"""
        nudges = []
        
        # Get last activity
        last_progress = self.session.query(StudentProgress).filter(
            StudentProgress.id_student == student_id
        ).order_by(StudentProgress.started_at.desc()).first()
        
        if last_progress:
            days_inactive = (datetime.utcnow() - last_progress.started_at).days
            
            # Nudge after 3+ days of inactivity (based on Himmler et al., 2019)
            if days_inactive >= 3:
                points = self.session.query(StudentPoints).filter(
                    StudentPoints.id_student == student_id
                ).first()
                
                streak = points.current_streak if points else 0
                
                message = random.choice(self.nudge_templates['inactivity'])
                message = message.format(
                    name="Student", 
                    days=days_inactive,
                    streak=streak
                )
                
                nudges.append({
                    'type': 'inactivity',
                    'priority': 'high' if days_inactive > 7 else 'medium',
                    'message': message,
                    'action_url': '/dashboard',
                    'timing': 'immediate'
                })
        
        return nudges
    
    def _check_deadlines(self, student_id):
        """Check for approaching deadlines"""
        nudges = []
        
        # Get active commitments
        upcoming = self.session.query(Commitment, LearningContent).join(
            LearningContent, Commitment.content_id == LearningContent.id
        ).filter(
            and_(
                Commitment.id_student == student_id,
                Commitment.status == 'pending',
                Commitment.committed_datetime <= datetime.utcnow() + timedelta(hours=24),
                Commitment.committed_datetime > datetime.utcnow()
            )
        ).all()
        
        for commit, content in upcoming:
            hours_left = (commit.committed_datetime - datetime.utcnow()).total_seconds() / 3600
            
            message = random.choice(self.nudge_templates['deadline_approaching'])
            message = message.format(
                content=content.title,
                hours=int(hours_left)
            )
            
            nudges.append({
                'type': 'deadline',
                'priority': 'high' if hours_left < 6 else 'medium',
                'message': message,
                'action_url': f'/content/{content.id}',
                'timing': 'immediate',
                'commitment_id': commit.id
            })
        
        return nudges
    
    def _check_missed_commitments(self, student_id):
        """Check for recently missed commitments"""
        nudges = []
        
        # Get commitments missed in last 24 hours
        recent_missed = self.session.query(Commitment, LearningContent).join(
            LearningContent, Commitment.content_id == LearningContent.id
        ).filter(
            and_(
                Commitment.id_student == student_id,
                Commitment.status == 'broken',
                Commitment.updated_at >= datetime.utcnow() - timedelta(hours=24)
            )
        ).all()
        
        for commit, content in recent_missed[:2]:  # Max 2 missed commitment nudges
            message = random.choice(self.nudge_templates['missed_commitment'])
            message = message.format(content=content.title)
            
            nudges.append({
                'type': 'missed_commitment',
                'priority': 'medium',
                'message': message,
                'action_url': f'/recommit/{commit.id}',
                'timing': 'next_login'
            })
        
        return nudges
    
    def _check_streak_risk(self, student_id):
        """Check if student's streak is at risk (loss aversion nudge)"""
        nudges = []
        
        points = self.session.query(StudentPoints).filter(
            StudentPoints.id_student == student_id
        ).first()
        
        if not points or points.current_streak == 0:
            return nudges
        
        # Check if they haven't completed anything today
        if points.last_commitment_date:
            days_since = (datetime.utcnow().date() - points.last_commitment_date.date()).days
            
            # Streak at risk if no activity today and it's past 6pm
            if days_since >= 1 or datetime.utcnow().hour >= 18:
                message = random.choice(self.nudge_templates['loss_aversion'])
                message = message.format(
                    streak=points.current_streak,
                    points=points.total_points
                )
                
                nudges.append({
                    'type': 'streak_risk',
                    'priority': 'high',  # Loss aversion = high priority (Karle et al., 2022)
                    'message': message,
                    'action_url': '/quick-win',  # Link to easiest available content
                    'timing': 'immediate'
                })
        
        return nudges
    
    def _check_progress_milestones(self, student_id):
        """Check for progress milestones to celebrate"""
        nudges = []
        
        # Get completion count
        completed_count = self.session.query(StudentProgress).filter(
            and_(
                StudentProgress.id_student == student_id,
                StudentProgress.status == 'completed'
            )
        ).count()
        
        total_content = self.session.query(LearningContent).count()
        
        # Celebrate milestones: 5, 10, 15 items OR 25%, 50%, 75%
        milestones = [5, 10, 15]
        percent_milestones = [25, 50, 75]
        
        if completed_count in milestones:
            message = self.nudge_templates['progress_celebration'][0]
            message = message.format(
                completed=completed_count,
                total=total_content
            )
            
            nudges.append({
                'type': 'celebration',
                'priority': 'low',  # Positive reinforcement, not urgent
                'message': message,
                'action_url': '/achievements',
                'timing': 'next_login'
            })
        
        return nudges
    
    def _prioritize_nudges(self, nudges):
        """Prioritize nudges to avoid overwhelming student"""
        # Sort by priority: high > medium > low
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        nudges.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        return nudges
    
    def _get_student_behavior(self, student_id):
        """Get student behavior data"""
        return self.session.query(StudentBehavior).filter(
            StudentBehavior.id_student == student_id
        ).first()
    
    def get_personalized_nudge(self, student_id, context='dashboard'):
        """
        Get single most relevant nudge for current context
        
        Contexts: 'dashboard', 'login', 'content_view', 'deadline_near'
        """
        all_nudges = self.check_and_send_nudges(student_id)
        
        if not all_nudges:
            return None
        
        # Filter by timing
        if context == 'login':
            relevant = [n for n in all_nudges if n['timing'] in ['immediate', 'next_login']]
        else:
            relevant = [n for n in all_nudges if n['timing'] == 'immediate']
        
        return relevant[0] if relevant else None
    
    def close(self):
        self.session.close()

