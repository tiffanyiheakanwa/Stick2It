from database_setup import (
    get_session, Student, StudentProgress,
    Commitment, StudentPoints, Task, TaskEvent
)
from logger import logger
from utils import safe_execute

class PrivacyService:
    def __init__(self):
        self.session = get_session()

    def delete_user_data(self, user_id):
        """
        Soft delete user data (GDPR-style)
        """
        logger.info(f"Soft deleting user data for {user_id}")

        def _internal():
            student = self.session.query(Student).filter_by(id=user_id).first()
            if not student:
                return {"error": "User not found"}

            # Disable account
            student.is_active = False
            student.email = f"deleted_{user_id}@anon.local"
            student.name = "Deleted User"

            # Soft delete related data
            self.session.query(Task).filter_by(user_id=user_id).delete()
            self.session.query(StudentProgress).filter_by(id_student=user_id).delete()
            self.session.query(Commitment).filter_by(id_student=user_id).delete()
            self.session.query(StudentPoints).filter_by(id_student=user_id).delete()

            self.session.commit()

            logger.info(f"User {user_id} data anonymized")
            return {"success": True, "message": "User data deleted (soft)"}

        return safe_execute(_internal)

    def opt_out_model(self, user_id):
        """
        User opts out of ML predictions
        """
        logger.info(f"User {user_id} opted out of ML model")

        def _internal():
            student = self.session.query(Student).filter_by(id=user_id).first()
            if not student:
                return {"error": "User not found"}

            student.model_opt_out = True
            self.session.commit()

            return {"success": True, "model_opt_out": True}

        return safe_execute(_internal)

    def no_nudges_mode(self, user_id):
        """
        Temporarily disable nudges
        """
        logger.info(f"User {user_id} disabled nudges")

        def _internal():
            student = self.session.query(Student).filter_by(id=user_id).first()
            if not student:
                return {"error": "User not found"}

            student.no_nudges = True
            self.session.commit()

            return {"success": True, "nudges_disabled": True}

        return safe_execute(_internal)
