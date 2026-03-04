# crud.py
from sqlalchemy.orm import Session
from . import models, schemas

def create_student_assignment(db: Session, assignment: schemas.AssignmentCreate, student_id: int):
    # 1. Create the Assignment
    db_assignment = models.Assignment(
        title=assignment.title,
        due_date=assignment.due_date,
        student_id=student_id,
        status="Pending"
    )
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)

    # 2. Create the Commitment (The Stake & Buddy)
    db_commitment = models.Commitment(
        assignment_id=db_assignment.id,
        stake_type=assignment.stake_type,
        stake_value=assignment.stake_value,
        buddy_name=assignment.buddy_name,
        buddy_email=assignment.buddy_email
    )
    db.add(db_commitment)
    db.commit()
    
    return db_assignment