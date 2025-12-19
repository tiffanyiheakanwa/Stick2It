"""
Hybrid Commitment Device System (Integrity-Enforced)
"""

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker
from database_setup_content import (
    Commitment, StudentPoints, AccountabilityPartner, LearningContent
)
from datetime import datetime, timedelta
from logger import logger
from utils import safe_execute

class CommitmentSystem:
    def __init__(self):
        engine = create_engine("sqlite:///procrastination.db")
        Session = sessionmaker(bind=engine)
        self.session = Session()

    def create_commitment(self, student_id, content_id, committed_datetime,
                          commitment_type="start_time"):
        logger.info(f"Creating commitment for student {student_id}, content {content_id}")

        if committed_datetime <= datetime.utcnow():
            return {"success": False, "error": "Commitment time must be in the future"}

        content = self.session.query(LearningContent).filter(
            LearningContent.id == content_id
        ).first()

        if not content:
            return {"success": False, "error": "Content not found"}

        points_map = {"easy": 5, "medium": 10, "hard": 15}
        points = points_map.get(content.difficulty, 10)

        commitment = Commitment(
            id_student=student_id,
            content_id=content_id,
            commitment_type=commitment_type,
            committed_datetime=committed_datetime,
            pledge_text=f"I will complete '{content.title}' by {committed_datetime}",
            points_at_stake=points,
            status="pending"
        )

        self.session.add(commitment)
        self._update_student_points(student_id, new_commitment=True)
        self.session.commit()
        logger.info(f"Commitment created with ID {commitment.id} for student {student_id}")
        return {
            "success": True,
            "commitment_id": commitment.id,
            "points_at_stake": points
        }

    def check_commitment(self, commitment_id, actual_action_time=None):
        """Check commitment ONLY after deadline"""
        logger.info(f"Checking commitment {commitment_id}")
        commitment = self.session.query(Commitment).filter(
            Commitment.id == commitment_id
        ).first()

        if not commitment:
            return {"success": False, "error": "Commitment not found"}

        if commitment.status != "pending":
            return {"success": True, "status": commitment.status}

        now = actual_action_time or datetime.utcnow()

        if now < commitment.committed_datetime:
            return {
                "success": True,
                "status": "pending",
                "message": "Deadline not reached"
            }

        grace = timedelta(hours=1)

        if now <= commitment.committed_datetime + grace:
            commitment.status = "kept"
            self._update_student_points(
                commitment.id_student,
                kept_commitment=True,
                points_change=commitment.points_at_stake
            )
            result = "kept"
        else:
            commitment.status = "broken"
            self._update_student_points(
                commitment.id_student,
                broken_commitment=True,
                points_change=-commitment.points_at_stake
            )
            result = "broken"

        commitment.completed_at = now
        self.session.commit()

        self._notify_partner(commitment.id_student, commitment, result)
        logger.info(f"Commitment {commitment_id} checked. Status: {result}")
        return {"success": True, "status": result}

    def _update_student_points(self, student_id, new_commitment=False,
                               kept_commitment=False, broken_commitment=False,
                               points_change=0):

        points = safe_execute(self.session.query(StudentPoints).filter(
            StudentPoints.id_student == student_id
        ).first())

        if not points:
            points = StudentPoints(
                id_student=student_id,
                total_points=100,
                current_streak=0,
                longest_streak=0
            )
            self.session.add(points)

        if new_commitment:
            points.total_commitments += 1

        if kept_commitment:
            points.kept_commitments += 1
            points.total_points = max(0, points.total_points + points_change)
            points.points_earned += points_change

            today = datetime.utcnow().date()
            if points.last_commitment_date and (
                today - points.last_commitment_date.date()
            ).days == 1:
                points.current_streak += 1
            else:
                points.current_streak = 1

            points.longest_streak = max(
                points.longest_streak, points.current_streak
            )
            points.last_commitment_date = datetime.utcnow()

        if broken_commitment:
            points.broken_commitments += 1
            points.total_points = max(0, points.total_points + points_change)
            points.points_lost += abs(points_change)
            points.current_streak = 0

        self.session.commit()

    def get_student_stats(self, student_id):
        points = safe_execute(self.session.query(StudentPoints).filter(
            StudentPoints.id_student == student_id
        ).first())

        if not points:
            return {"total_points": 100, "current_streak": 0}

        return {
            "total_points": points.total_points,
            "current_streak": points.current_streak,
            "longest_streak": points.longest_streak,
            "success_rate": round(
                (points.kept_commitments or 0) /
                max(points.total_commitments or 1, 1) * 100, 1
            )
        }

    def add_accountability_partner(self, student_id, partner_name,
                                   partner_email=None, partner_phone=None):

        if not partner_email and not partner_phone:
            return {"success": False, "error": "Contact required"}

        existing = self.session.query(AccountabilityPartner).filter(
            and_(
                AccountabilityPartner.id_student == student_id,
                AccountabilityPartner.is_active == True
            )
        ).first()

        if existing:
            existing.is_active = False

        partner = AccountabilityPartner(
            id_student=student_id,
            partner_name=partner_name,
            partner_email=partner_email,
            partner_phone=partner_phone
        )

        self.session.add(partner)
        self.session.commit()

        return {"success": True, "partner_id": partner.id}

    # def _notify_partner(self, student_id, commitment, status):
    #     # MVP: console-only
    #     print(f"📣 Partner notified: commitment {status}")

    def _notify_partner(self, student_id, commitment, status):
        """Send notification to accountability partner"""
        
        partner = safe_execute(self.session.query(AccountabilityPartner).filter(
            and_(
                AccountabilityPartner.id_student == student_id,
                AccountabilityPartner.is_active == True
            )
        ).first())  
        
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