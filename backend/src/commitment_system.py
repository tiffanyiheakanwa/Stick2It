import uuid
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.database import get_db_session
from backend.app.models import Assignment, Commitment, StudentPoints, Student, Nudge
from .logger import logger
from backend.app.config import serializer, SECURITY_SALT
from .email_utils import send_sendgrid_email

class CommitmentSystem:
    def __init__(self):
        """
        Initializes the system with a database session.
        """
        pass

    def create_commitment(self, student_id, committed_datetime, custom_title=None, 
                      buddy_email=None, buddy_name=None, stake_value=10, 
                      stake_type="Points",
                     penalty_message=None, content_id=None):
        """
        Creates a high-stakes commitment linked to an assignment.
        Generates a unique verification token for the Accountability Partner.
        """
        logger.info(f"Creating {stake_type} commitment for student {student_id}")
        with get_db_session() as session:

            # 2. Generate unique token for Buddy Verification Link
            verification_token = str(uuid.uuid4())

            # 3. Create the Commitment record
            new_commitment = Commitment(
                student_id=student_id,
                content_id=content_id,
                stake_type=stake_type,
                custom_title=custom_title, 
                stake_value=stake_value,
                penalty_message=penalty_message or f"Lose {stake_value} points if {custom_title} is not completed by {committed_datetime}",
                buddy_name=buddy_name,
                buddy_email=buddy_email,
                verification_token=verification_token,
                committed_datetime=committed_datetime,
                status="pending"
            )

            session.add(new_commitment)
            self._ensure_points_record(session, student_id)
            session.commit()
            session.refresh(new_commitment) # Ensure ID is loaded

            # 4. Initialize points if this is a points-based stake
            if stake_type == "Points":
                self._initialize_points_record(session, student_id)
            
            # 5. Notify the partner immediately that the contract is locked
            self._send_initial_buddy_alert(new_commitment)

            return {
                "success": True, 
                "commitment_id": new_commitment.id,
                "verification_token": verification_token
            }

    def check_commitment(self, commitment_id, actual_action_time=None, allow_grace_period=False):
        """
        Strictly enforces deadlines. If it's past the deadline, it's broken.
        """
        with get_db_session() as session:
            commitment = session.query(Commitment).filter(Commitment.id == commitment_id).first()

            if not commitment or commitment.status not in ["pending", "requires_stake", "in_progress", "awaiting_verification"]:
                return {"success": False, "error": "Invalid or inactive commitment"}

            now = actual_action_time or datetime.utcnow()
            if commitment.assignment:
                deadline = commitment.assignment.due_date
            else:
                deadline = commitment.committed_datetime    
                        
            # Strict Integrity Enforcement
            if deadline and now > deadline:
                if commitment.status == "requires_stake":
                    commitment.status = "expired"
                    session.commit()
                    return {"success": True, "status": "expired"}
                else:
                    # Dynamic grace period based on student lenience profile
                    lenience_hours = getattr(commitment.student, 'grace_period_lenience', 1.0)
                    if now <= (deadline + timedelta(hours=lenience_hours)):
                        return {"success": True, "status": "pending", "message": "In grace period"}
                    else:
                        return self._process_failure(session, commitment)
            
            return {"success": True, "status": commitment.status}

    def verify_commitment(self, token):
        """
        Called when a Buddy clicks the verification link. 
        Releases the stake and updates student streaks.
        """
        with get_db_session() as session:
            commitment = session.query(Commitment).filter(Commitment.verification_token == token).first()
            
            if not commitment:
                return {"success": False, "error": "Invalid verification token"}

            if commitment.status != "pending":
                return {"success": True, "status": commitment.status}

            commitment.is_verified_by_buddy = True
            commitment.status = "kept"
            commitment.assignment.status = "Completed"
            commitment.completed_at = datetime.utcnow()
            
            # Update Points and Streaks for Success
            points = session.query(StudentPoints).filter(
                StudentPoints.student_id == commitment.student_id
            ).first()

            if points:
                points.total_points += commitment.stake_value
                points.current_streak += 1
                points.longest_streak = max(points.longest_streak, points.current_streak)
                points.last_commitment_date = datetime.utcnow()

            self._notify_partner(commitment, result="kept")
            return {"success": True, "message": "Commitment verified! Points released and streak updated."}

    def _process_failure(self, session,  commitment):
        """Executes the penalty and notifies the partner of the failure."""
        logger.warning(f" Commitment {commitment.id} BROKEN. Executing penalties.")
        commitment.status = "broken"
        
        # Immediate Point Deduction and Streak Reset
        self._update_student_stats(session, commitment.student_id, success=False, points_change=commitment.stake_value)

        # Execute Social Stake: Notify partner with the specific penalty
        self._notify_partner(commitment, result="broken")
        
        return {"success": True, "status": "broken", "penalty_executed": True}

    def get_student_stats(self, student_id):
        with get_db_session() as session:
            commitments = session.query(Commitment).filter(
                Commitment.student_id == student_id,
                Commitment.status != 'expired'
            ).order_by(Commitment.committed_datetime.desc()).all()
            
            # Lazily evaluate deadlines to ensure frontend is always up to date
            from datetime import timezone
            now = datetime.now(timezone.utc)
            valid_commitments = []
            for c in commitments:
                deadline = c.assignment.due_date if c.assignment else c.committed_datetime
                if deadline:
                    deadline_aware = deadline if deadline.tzinfo else deadline.replace(tzinfo=timezone.utc)
                    if now > deadline_aware:                    
                        if c.status == 'requires_stake':
                            c.status = 'expired'
                            session.commit()
                            continue # Skip adding to valid_commitments
                        elif c.status in ['pending', 'in_progress']:
                            self._process_failure(session, c)
                            session.commit()
                            valid_commitments.append(c)
                        else:
                            valid_commitments.append(c)
                    else:
                        valid_commitments.append(c)
            
            points_record = session.query(StudentPoints).filter(
                StudentPoints.student_id == student_id
            ).first()
            current_streak = points_record.current_streak if points_record else 0
            total_points = points_record.total_points if points_record else 0
            
            return {
                "success": True,
                "streak": current_streak,
                "points": total_points,
                "commitments": [
                    {
                        "id": c.id,
                        "status": c.status,
                        "stake_value": c.stake_value,
                        "stake_type": c.stake_type,
                        "buddy_name": c.buddy_name,
                        "penalty_message": c.penalty_message,
                        "committed_datetime": c.committed_datetime.isoformat() if c.committed_datetime else None,
                        "completed_at": c.completed_at.isoformat() if c.completed_at else (c.updated_at.isoformat() if c.updated_at else None),
                        "title": c.assignment.title if c.assignment else (c.custom_title or "Task"),
                        "source_platform": c.assignment.source_platform if c.assignment else "local"
                    } for c in valid_commitments
                ]
            }

    def _update_student_stats(self, session, student_id, success, points_change=0):
        """
        Updates long-term success rate for AI and point streaks for gamification.
        """
        # 1. Update AI success rate
        student = session.query(Student).filter(Student.id == student_id).first()
        if student:
            rate = 1.0 if success else 0.0
            student.avg_success_rate = (student.avg_success_rate + rate) / 2

        # 2. Update Points and Streaks
        points = session.query(StudentPoints).filter(StudentPoints.student_id == student_id).first()
        if not points:
            points = StudentPoints(student_id=student_id, total_points=100)
            session.add(points)

        if success:
            points.total_points += points_change
            points.current_streak += 1
            points.longest_streak = max(points.longest_streak, points.current_streak)
            points.last_commitment_date = datetime.utcnow()
        else:
            # Loss Aversion: Deduct points immediately and reset streak
            points.total_points = max(0, points.total_points - points_change)
            points.current_streak = 0

    def _initialize_points_record(self, session, student_id):
        """Ensures the student has a points entry to track streaks."""
        points = session.query(StudentPoints).filter(StudentPoints.student_id == student_id).first()
        if not points:
            new_points = StudentPoints(student_id=student_id, total_points=100)
            session.add(new_points)

    def _ensure_points_record(self, session, student_id):
        """Ensures the student has a points entry."""
        points = session.query(StudentPoints).filter(StudentPoints.student_id == student_id).first()
        if not points:
            session.add(StudentPoints(student_id=student_id, total_points=100))

    def _send_initial_buddy_alert(self, commitment):
        """Initial notification to buddy that a contract has been locked."""
        verification_url = f"http://localhost:5173/verify/{commitment.verification_token}"
        subject = f"Action Required: Accountability Partner for {commitment.buddy_name}"
        task_title = commitment.assignment.title if commitment.assignment else (commitment.custom_title or "a task")
        body = f"Your friend committed to: {task_title}\nStake: {commitment.stake_type}\nPenalty: {commitment.penalty_message}\nVerify here: {verification_url}"
        self._send_email(commitment.buddy_email, subject, body)

    def _send_verification_request_alert(self, commitment):
        """Notification to buddy that the user claims they are done and needs verification."""
        verification_url = f"http://localhost:5173/verify/{commitment.verification_token}"
        subject = f"Verification Required: {commitment.student.name} claims they finished their task"
        task_title = commitment.assignment.title if commitment.assignment else (commitment.custom_title or "a task")
        body = f"Your friend {commitment.student.name} claims they completed: {task_title}\nStake: {commitment.stake_type}\nVerify if they actually did it here: {verification_url}"
        self._send_email(commitment.buddy_email, subject, body)

    def _notify_partner(self, commitment, result):
        """Notifies partner of completion or failure."""
        student_name = commitment.student.name
        if result == 'broken':
            subject = f" {student_name} missed their commitment"
            body = f"Penalty Action Required: {commitment.penalty_message}"
        else:
            subject = f" {student_name} kept their commitment!"
            body = f"They finished {commitment.assignment.title}. Great job!"
        self._send_email(commitment.buddy_email, subject, body)

    def generate_verification_link(self, commitment_id: int):
            # This token is signed and contains the ID
            token = serializer.dumps(commitment_id, salt=SECURITY_SALT)
            # In production, use your actual domain
            return f"http://localhost:8000/verify/{token}"

    def _send_email(self, to_email, subject, body):
        """Dispatches the buddy email via SendGrid."""
        send_sendgrid_email(to_email, subject, body, "Accountability Partner")