"""
Smart Nudging System - Just-in-Time Adaptive Interventions
"""
from sqlalchemy import and_, or_
from datetime import datetime, timedelta
import random
from .logger import logger
from backend.app.database import get_db_session
from backend.app.models import (
    Student, 
    StudentProgress, 
    Commitment, 
    StudentPoints, 
    LearningContent, 
    StudentBehavior, 
    Nudge,
    Prediction
)
import random
from backend.app.database import get_db_session
from backend.app.models import StudentBehavior, Student
from .predict import ProcrastinationPredictor # Import the ML predictor

class SmartNudgeSystem:
    def __init__(self):
        self.sent_cache = {}
        # Initialize the ML Predictor
        self.predictor = ProcrastinationPredictor() 
        
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
    
    def _can_send(self, student_id, nudge_type):
        key = (student_id, nudge_type)
        last = self.sent_cache.get(key)

        if not last:
            return True

        return datetime.utcnow() - last > timedelta(hours=24)

    def _mark_sent(self, student_id, nudge_type):
        self.sent_cache[(student_id, nudge_type)] = datetime.utcnow()

    def check_and_send_nudges(self, student_id):
        """
        Refactored: Triggers nudges based on actual AI risk scores.
        """
        with get_db_session() as session:
            logger.info(f"🧠 AI Checking risk for student {student_id}")
            
            # Calculate the real P_fail using the ML model
            p_fail = self.calculate_pfail(session, student_id)

            # 1. Get all pending commitments for this student
            active_commitments = session.query(Commitment).filter(
                and_(Commitment.student_id == student_id, Commitment.status == 'pending')
            ).all()

            nudges_to_send = []

            for commit in active_commitments:
                # # 2. Calculate dynamic risk
                # p_fail = self.calculate_pfail(commit)
                # 3. Log the prediction for future ML training (ml_ready.csv)
                self._log_prediction(student_id, commit.assignment_id, p_fail)

                # 4. Trigger logic: Threshold of 0.75
                if p_fail >= 0.75:
                    hours_left = int((commit.assignment.due_date - datetime.utcnow()).total_seconds() / 3600)
                    message = random.choice(self.nudge_templates['deadline_approaching']).format(
                        content=commit.assignment.title,
                        hours=hours_left
                    )
                    
                    nudges_to_send.append({
                        'type': 'AI_DYNAMIC_RISK',
                        'p_fail': p_fail,
                        'message': message,
                        'assignment_id': commit.assignment_id
                    })

            # Execute and log the top priority nudge
            if nudges_to_send:
                top_nudge = max(nudges_to_send, key=lambda x: x['p_fail'])
                self._send_personalized_alert(
                    student_id, 
                    top_nudge['type'], 
                    top_nudge['message'], 
                    top_nudge['assignment_id']
                )
            return nudges_to_send

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
        logger.info(f"Checking deadlines for student {student_id}")
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
        student = self.session.query(Student).filter_by(id=student_id).first()
        if student and student.no_nudges:
            return None

        all_nudges = self.check_and_send_nudges(student_id)
        
        if not all_nudges:
            return None
        
        # Filter by timing
        if context == 'login':
            relevant = [n for n in all_nudges if n['timing'] in ['immediate', 'next_login']]
        else:
            relevant = [n for n in all_nudges if n['timing'] == 'immediate']
        
        return relevant[0] if relevant else None
    
    def calculate_pfail(self, session, student_id):
        """
        REPLACED MOCK LOGIC: Now uses the Random Forest model to predict risk
        based on real-time student behavior data.
        """
        try:
            # 1. Fetch the student's current behavioral features
            behavior = session.query(StudentBehavior).filter(
                StudentBehavior.student_id == student_id
            ).first()

            if not behavior:
                logger.warning(f"No behavior data for student {student_id}. Falling back to default.")
                return 0.5

            # 2. Extract features into the format expected by the model
            features = {
                'last_minute_ratio': behavior.last_minute_ratio,
                'engagement_intensity': behavior.engagement_intensity,
                'deadline_pressure': behavior.deadline_pressure,
                'login_consistency': behavior.login_consistency,
                'early_starter': behavior.early_starter,
                'completion_rate': behavior.completion_rate,
                'activity_span': behavior.activity_span
            }

            # 3. Get the prediction probability from the ML model
            # probability_high_risk is the raw float (0.0 to 1.0)
            prediction_result = self.predictor.predict_risk(features)
            p_fail = prediction_result['probability_high_risk']

            return p_fail

        except Exception as e:
            logger.error(f"AI Prediction failed for student {student_id}: {e}")
            return 0.5 # Safe default in case of model error
        # """
        # Calculates a mock Probability of Failure (P_fail).
        # Formula: (Work Required / Time Remaining) adjusted by student's historical success.
        # """
        # now = datetime.utcnow()
        # deadline = commitment.assignment.due_date
        # created_at = commitment.created_at
        
        # total_window = (deadline - created_at).total_seconds()
        # time_remaining = (deadline - now).total_seconds()
        
        # if time_remaining <= 0:
        #     return 1.0 # Deadline passed
            
        # # Estimate complexity based on stake (higher points = higher complexity)
        # # Scale 1-10 points to a 'work units' factor
        # work_required_factor = max(1, commitment.stake_value / 5) 
        
        # # Basic Risk: How much of the window is left vs. complexity
        # # A value > 1.0 means the student is mathematically 'behind'
        # time_ratio = time_remaining / total_window
        # risk_score = (work_required_factor * (1 - time_ratio))
        
        # # Adjust by student's historical success rate (Inverse relationship)
        # # If they succeed 90% of the time, risk decreases
        # student_factor = 1.2 - (commitment.student.avg_success_rate or 0.5)
        
        # final_p_fail = min(0.99, max(0.01, risk_score * student_factor))
        # return round(final_p_fail, 2)
    
    def trigger_streak_protection_cycle(self, student_id):
            """
            Identifies students who have not completed a task today 
            and are at risk of losing a 3+ day streak.
            """
            logger.info(f"Checking streak risk for student {student_id}...")
            
            with get_db_session() as session:
                points = session.query(StudentPoints).filter(
                    StudentPoints.student_id == student_id
                ).first()
                
                # FIXED: All logic must stay inside the 'with' block to access 'points'
                if points and points.current_streak >= 3:
                    today = datetime.utcnow().date()
                    last_activity = points.last_commitment_date.date() if points.last_commitment_date else None
                    
                    # FIXED: Correct indentation so last_activity is recognized
                    if last_activity != today:
                        # Trigger Loss Aversion Nudge
                        message = random.choice(self.nudge_templates['loss_aversion'])
                        message = message.format(
                            streak=points.current_streak,
                            points=points.total_points
                        )
                        
                        # FIXED: Added 'session' as the first argument as required by your new architecture
                        self._send_personalized_alert(session, points.student_id, "STREAK_PROTECTION", message)
                        logger.info(f"🔥 Streak protection nudge sent to student {points.student_id}")

    def _send_personalized_alert(self, session, student_id, nudge_type, message, assignment_id=None):
        """
        Logs the nudge in the database for AI training and triggers delivery.
        """
        try:
            # Create a record in the Nudges table
            new_nudge = Nudge(
                student_id=student_id,
                assignment_id=assignment_id,
                message=message,
                nudge_type=nudge_type,
                sent_at=datetime.utcnow()
            )
            session.add(new_nudge)
            session.commit()
            
            # TODO: Add your actual email/push notification delivery logic here
            logger.info(f"✅ Nudge successfully logged for student {student_id}")
        except Exception as e:
            logger.error(f"❌ Failed to log nudge: {e}")
            
        except Exception as e:
            self.session.rollback()
            logger.error(f"❌ Failed to log nudge: {e}")

    def _log_prediction(self, session, student_id, assignment_id, p_fail):
        """
        Logs every AI calculation. This becomes the training data for Phase 4.
        """
        from .models import Prediction # Ensure Prediction is imported
        
        new_pred = Prediction(
            student_id=student_id,
            assignment_id=assignment_id,
            risk_score=p_fail, # Changed from 'risk_level' to Float score
            predicted_at=datetime.utcnow()
        )
        session.add(new_pred)
        session.commit()

    def close(self):
        self.session.close()

