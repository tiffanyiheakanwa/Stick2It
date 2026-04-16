import datetime
import requests
from sqlalchemy.orm import Session
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from backend.app.models import Assignment, Student
from backend.src.logger import logger

class AssignmentIngestor:
    def __init__(self, session: Session):
        self.session = session

    def sync_for_student(self, student_id: int):
        student = self.session.get(Student, student_id)
        if not student:
            return {"success": False, "error": "Student not found"}
        
        if student.auth_provider == "google" and student.ext_access_token:
            return self._sync_google_classroom(student)
        elif student.auth_provider == "moodle" and student.ext_access_token:
            return self._sync_moodle(student)
        
        return {"success": False, "error": "No valid external auth provider found"}

    def _sync_google_classroom(self, student: Student):
        try:
            creds = Credentials(token=student.ext_access_token)
            service = build('classroom', 'v1', credentials=creds)
            
            # Fetch active courses for the student
            courses_result = service.courses().list(studentId='me', courseStates=['ACTIVE']).execute()
            courses = courses_result.get('courses', [])
            
            if not courses:
                return {"success": True, "synced_count": 0, "message": "No active courses found."}
                
            synced_count = 0
            
            for course in courses:
                course_id = course.get('id')
                # Fetch course-work (assignments)
                work_result = service.courses().courseWork().list(courseId=course_id).execute()
                works = work_result.get('courseWork', [])
                
                for work in works:
                    work_id = work.get('id')
                    title = work.get('title', 'Untitled Google Assignment')
                    description = work.get('description', '')
                    
                    # Parse due date if available
                    due_date = None
                    if 'dueDate' in work:
                        d_info = work['dueDate']
                        t_info = work.get('dueTime', {})
                        try:
                            due_date = datetime.datetime(
                                year=d_info.get('year'),
                                month=d_info.get('month'),
                                day=d_info.get('day'),
                                hour=t_info.get('hours', 23),
                                minute=t_info.get('minutes', 59),
                                tzinfo=datetime.timezone.utc
                            )
                        except Exception:
                            due_date = None
                            
                    self._upsert_assignment(
                        student_id=student.id,
                        external_id=f"g_classroom_{work_id}",
                        source_platform="google",
                        title=title,
                        description=description,
                        due_date=due_date
                    )
                    synced_count += 1
                    
            self.session.commit()
            return {"success": True, "synced_count": synced_count}
            
        except HttpError as error:
            # 401 Unauthorized implies Token is expired or revoked
            if error.resp.status == 401:
                return {"success": False, "error": "Google token expired. Please re-login.", "needs_reauth": True}
            logger.error(f"Google Classroom API Error: {error}")
            return {"success": False, "error": "An error occurred with Google APIs"}
        except Exception as e:
            logger.error(f"Ingestion Error: {e}")
            return {"success": False, "error": str(e)}

    def _sync_moodle(self, student: Student):
        # Moodle fetching logic Placeholder - typically relies on standard webservice actions
        # For now, just bypass natively.
        return {"success": True, "synced_count": 0, "message": "Moodle sync not fully implemented yet."}

    def _upsert_assignment(self, student_id: int, external_id: str, source_platform: str, title: str, description: str, due_date: datetime.datetime):
        # Deduplication check
        existing = self.session.query(Assignment).filter_by(
            student_id=student_id,
            external_id=external_id,
            source_platform=source_platform
        ).first()

        if existing:
            # Update values seamlessly without losing commitments mapped to it!
            existing.title = title
            existing.description = description
            existing.due_date = due_date
        else:
            # Insert entirely new mapping
            new_assign = Assignment(
                student_id=student_id,
                title=title,
                description=description,
                due_date=due_date,
                status="Pending",
                source_platform=source_platform,
                external_id=external_id
            )
            self.session.add(new_assign)
            self.session.flush() # assign ID
            
            # Predict Risk and Create Pre-Commitment
            try:
                from backend.src.predict import ProcrastinationPredictor
                from backend.app.models import Prediction, Commitment
                import uuid
                import datetime as dt

                predictor = ProcrastinationPredictor()
                result = predictor.predict_from_task(title, student_id)
                
                new_pred = Prediction(
                    student_id=student_id,
                    assignment_id=new_assign.id,
                    risk_score=result['probability_high_risk'],
                    predicted_at=dt.datetime.utcnow()
                )
                self.session.add(new_pred)
                
                pre_commit = Commitment(
                    student_id=student_id,
                    assignment_id=new_assign.id,
                    status='requires_stake',
                    stake_value=10,
                    verification_token=str(uuid.uuid4()),
                    committed_datetime=due_date or dt.datetime.utcnow(),
                    stake_type="Points"
                )
                self.session.add(pre_commit)
            except Exception as e:
                logger.error(f"Failed to auto-predict new assignment {title}: {e}")
