"""
Hybrid Commitment Device System
Combines: Soft pledges + Streaks + Points + Accountability partners
"""
from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from database_setup import (Commitment, StudentPoints, AccountabilityPartner,
                            StudentProgress, LearningContent)
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class CommitmentSystem:
    def __init__(self):
        engine = create_engine('sqlite:///procrastination.db')
        Session = sessionmaker(bind=engine)
        self.session = Session()
    
    def create_commitment(self, student_id, content_id, committed_datetime, 
                         commitment_type='start_time'):
        """
        Student makes a soft pledge
        
        Parameters:
        -----------
        student_id : int
        content_id : int
        committed_datetime : datetime - When they commit to start/finish
        commitment_type : str - 'start_time' or 'completion_deadline'
        """
        # Get content details
        content = self.session.query(LearningContent).filter(
            LearningContent.id == content_id
        ).first()
        
        if not content:
            return {'success': False, 'error': 'Content not found'}
        
        # Create pledge text
        action = "start" if commitment_type == 'start_time' else "complete"
        pledge_text = f"I will {action} '{content.title}' by {committed_datetime.strftime('%b %d at %I:%M %p')}"
        
        # Calculate points at stake (harder tasks = more points)
        points_map = {'easy': 5, 'medium': 10, 'hard': 15}
        points = points_map.get(content.difficulty, 10)
        
        # Create commitment
        commitment = Commitment(
            id_student=student_id,
            content_id=content_id,
            commitment_type=commitment_type,
            committed_datetime=committed_datetime,
            pledge_text=pledge_text,
            points_at_stake=points
        )
        
        self.session.add(commitment)
        
        # Update student's commitment count
        self._update_student_points(student_id, new_commitment=True)
        
        self.session.commit()
        
        return {
            'success': True,
            'commitment_id': commitment.id,
            'pledge': pledge_text,
            'points_at_stake': points,
            'committed_time': committed_datetime
        }
    
    def check_commitment(self, commitment_id, actual_action_time=None):
        """
        Check if student kept their commitment
        
        Parameters:
        -----------
        commitment_id : int
        actual_action_time : datetime - When they actually started/completed
        """
        commitment = self.session.query(Commitment).filter(
            Commitment.id == commitment_id
        ).first()
        
        if not commitment:
            return {'success': False, 'error': 'Commitment not found'}
        
        if actual_action_time is None:
            actual_action_time = datetime.utcnow()
        
        # Check if they kept it (within grace period of 1 hour)
        grace_period = timedelta(hours=1)
        deadline = commitment.committed_datetime + grace_period
        
        if actual_action_time <= deadline:
            # KEPT the commitment! 🎉
            commitment.status = 'kept'
            commitment.completed_at = actual_action_time
            
            # Award points
            points_earned = commitment.points_at_stake
            self._update_student_points(
                commitment.id_student,
                kept_commitment=True,
                points_change=points_earned
            )
            
            result = {
                'success': True,
                'status': 'kept',
                'message': f'Great job! You earned {points_earned} points! 🎉',
                'points_earned': points_earned
            }
        else:
            # BROKEN commitment 😢
            commitment.status = 'broken'
            
            # Lose points
            points_lost = commitment.points_at_stake
            self._update_student_points(
                commitment.id_student,
                broken_commitment=True,
                points_change=-points_lost
            )
            
            result = {
                'success': True,
                'status': 'broken',
                'message': f'You missed your commitment and lost {points_lost} points.',
                'points_lost': points_lost
            }
        
        self.session.commit()
        
        # Notify accountability partner if exists
        self._notify_partner(commitment.id_student, commitment, result['status'])
        
        return result
    
    def _update_student_points(self, student_id, new_commitment=False,
                               kept_commitment=False, broken_commitment=False,
                               points_change=0):
        """Update student's points and streaks"""
        
        # Get or create student points record
        student_points = self.session.query(StudentPoints).filter(
            StudentPoints.id_student == student_id
        ).first()
        
        if not student_points:
            student_points = StudentPoints(id_student=student_id)
            self.session.add(student_points)
        
        # Update based on action
        if new_commitment:
          student_points.total_commitments = (student_points.total_commitments or 0) + 1

        if kept_commitment:
          student_points.kept_commitments = (student_points.kept_commitments or 0) + 1
          student_points.total_points = (student_points.total_points or 0) + points_change
          student_points.points_earned = (student_points.points_earned or 0) + points_change

            
            # Update streak
          today = datetime.utcnow().date()
          if student_points.last_commitment_date:
                last_date = student_points.last_commitment_date.date()
                if (today - last_date).days == 1:
                    # Consecutive day!
                    student_points.current_streak += 1
                elif (today - last_date).days == 0:
                    # Same day, don't break streak
                    pass
                else:
                    # Streak broken
                    student_points.current_streak = 1
          else:
            student_points.current_streak = 1
            
            # Update longest streak
            if student_points.current_streak > student_points.longest_streak:
                student_points.longest_streak = student_points.current_streak
            
            student_points.last_commitment_date = datetime.utcnow()
        
        if broken_commitment:
            student_points.broken_commitments += 1
            student_points.total_points += points_change  # Negative value
            student_points.points_lost += abs(points_change)
            
            # Break streak
            student_points.current_streak = 0
        
        self.session.commit()
    
    def get_student_stats(self, student_id):
        """Get student's commitment stats"""
        
        student_points = self.session.query(StudentPoints).filter(
            StudentPoints.id_student == student_id
        ).first()
        
        if not student_points:
            return {
                'total_points': 100,
                'current_streak': 0,
                'longest_streak': 0,
                'success_rate': 0,
                'total_commitments': 0
            }
        
        return {
            'total_points': student_points.total_points,
            'points_earned': student_points.points_earned,
            'points_lost': student_points.points_lost,
            'current_streak': student_points.current_streak,
            'longest_streak': student_points.longest_streak,
            'success_rate': round(
                (student_points.kept_commitments or 0) / 
                max(student_points.total_commitments or 1, 1) * 100,
                1
            ),
            'total_commitments': student_points.total_commitments,
            'kept': student_points.kept_commitments,
            'broken': student_points.broken_commitments
        }
    
    def add_accountability_partner(self, student_id, partner_name, 
                                  partner_email=None, partner_phone=None):
        """Add an accountability partner"""
        
        if not partner_email and not partner_phone:
            return {'success': False, 'error': 'Need email or phone'}
        
        # Check if partner already exists
        existing = self.session.query(AccountabilityPartner).filter(
            and_(
                AccountabilityPartner.id_student == student_id,
                AccountabilityPartner.is_active == True
            )
        ).first()
        
        if existing:
          existing.is_active = False
          self.session.commit()

        
        partner = AccountabilityPartner(
            id_student=student_id,
            partner_name=partner_name,
            partner_email=partner_email,
            partner_phone=partner_phone
        )
        
        self.session.add(partner)
        self.session.commit()
        
        # Send verification email
        if partner_email:
            self._send_partner_verification(partner)
        
        return {
            'success': True,
            'partner_id': partner.id,
            'message': f'Added {partner_name} as accountability partner'
        }
    
    def _notify_partner(self, student_id, commitment, status):
        """Send notification to accountability partner"""
        
        partner = self.session.query(AccountabilityPartner).filter(
            and_(
                AccountabilityPartner.id_student == student_id,
                AccountabilityPartner.is_active == True
            )
        ).first()
        
        if not partner or not partner.partner_email:
            return
        
        # Get student name (for now, use ID)
        student_name = f"Student {student_id}"
        
        if status == 'kept' and partner.notify_on_completion:
            subject = f"🎉 {student_name} kept their commitment!"
            body = f"""
            Great news!
            
            {student_name} just completed: {commitment.pledge_text}
            
            They're doing great! Send them an encouraging message!
            
            - Stick2It App
            """
        elif status == 'broken' and partner.notify_on_miss:
            subject = f"😢 {student_name} missed their commitment"
            body = f"""
            Hey {partner.partner_name},
            
            {student_name} missed this commitment: {commitment.pledge_text}
            
            They could use some encouragement. Reach out and check in!
            
            - Stick2It App
            """
        else:
            return
        
        self._send_email(partner.partner_email, subject, body)
    
    def _send_partner_verification(self, partner):
        """Send verification email to partner"""
        
        subject = "You've been added as an Accountability Partner!"
        body = f"""
        Hi {partner.partner_name},
        
        Student {partner.id_student} has added you as their accountability partner on Stick2It!
        
        You'll receive notifications when they:
        - Complete commitments (so you can celebrate with them!)
        - Miss deadlines (so you can encourage them)
        
        You can reply to this email to confirm you're okay with this.
        
        Thank you for helping them succeed!
        
        - Stick2It Team
        """
        
        self._send_email(partner.partner_email, subject, body)
    
    def _send_email(self, to_email, subject, body):
        """
        Send email (simplified version for MVP)
        In production, use SendGrid or similar
        """
        print(f"\n📧 EMAIL NOTIFICATION:")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"Body:\n{body}")
        print("="*60)
        
        # TODO: Implement actual email sending
        # For now, just print to console
        # In production:
        # - Use SendGrid API
        # - Or SMTP with Gmail
        # - Or AWS SES
    
    def close(self):
        self.session.close()


# Test the system
if __name__ == "__main__":
    system = CommitmentSystem()
    
    student_id = 11391
    content_id = 1  # "Welcome & Overview"
    
    print("\n" + "="*60)
    print("COMMITMENT SYSTEM TEST")
    print("="*60)
    
    # 1. Add accountability partner
    print("\n1️⃣ Adding accountability partner...")
    result = system.add_accountability_partner(
        student_id=student_id,
        partner_name="Sarah Johnson",
        partner_email="tiffanyiheakanwa@gmail.com"
    )
    print(f"   {result['message']}")
    
    # 2. Create commitment
    print("\n2️⃣ Creating commitment...")
    commit_time = datetime.utcnow() + timedelta(hours=2)  # 2 hours from now
    result = system.create_commitment(
        student_id=student_id,
        content_id=content_id,
        committed_datetime=commit_time,
        commitment_type='start_time'
    )
    print(f"   Pledge: {result['pledge']}")
    print(f"   Points at stake: {result['points_at_stake']}")
    commitment_id = result['commitment_id']
    
    # 3. Simulate keeping the commitment (start on time)
    print("\n3️⃣ Simulating kept commitment...")
    result = system.check_commitment(
        commitment_id=commitment_id,
        actual_action_time=commit_time - timedelta(minutes=10)  # 10 min early!
    )
    print(f"   {result['message']}")
    
    # 4. Check stats
    print("\n4️⃣ Student stats:")
    stats = system.get_student_stats(student_id)
    print(f"   Total points: {stats['total_points']}")
    print(f"   Current streak: {stats['current_streak']} days 🔥")
    print(f"   Success rate: {stats['success_rate']}%")
    print(f"   Kept: {stats['kept']}/{stats['total_commitments']}")
    
    print("\n✅ Test complete!")
    print("="*60)
    
    system.close()