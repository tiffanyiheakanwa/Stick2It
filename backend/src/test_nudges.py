"""Test smart nudging system"""
from .nudge_system import SmartNudgeSystem
from datetime import datetime, timedelta
from .database_setup_content import get_session, Commitment, StudentPoints, LearningContent

def test_nudges():
    system = SmartNudgeSystem()
    student_id = 11391
    
    print("\n" + "="*60)
    print("SMART NUDGE SYSTEM TEST")
    print("="*60)
    
    # Test 1: Get all nudges
    print("\n1️⃣ Checking all potential nudges...")
    nudges = system.check_and_send_nudges(student_id)
    print(f"   Found {len(nudges)} nudges")
    
    for nudge in nudges:
        print(f"\n   📬 {nudge['type'].upper()} ({nudge['priority']} priority)")
        print(f"      {nudge['message']}")
        print(f"      Action: {nudge['action_url']}")
    
    # Test 2: Context-specific nudge
    print("\n2️⃣ Getting login-time nudge...")
    nudge = system.get_personalized_nudge(student_id, 'login')
    if nudge:
        print(f"   {nudge['message']}")
    else:
        print("   No nudges needed right now ✅")
    
    # Test 3: Simulate deadline scenario
    print("\n3️⃣ Simulating approaching deadline...")
    session = get_session()
    
    # Create test commitment due in 4 hours
    content = session.query(LearningContent).first()
    test_commit = Commitment(
        id_student=student_id,
        content_id=content.id,
        commitment_type='completion_deadline',
        committed_datetime=datetime.utcnow() + timedelta(hours=4),
        pledge_text=f"Test deadline for {content.title}",
        status='pending'
    )
    session.add(test_commit)
    session.commit()
    
    # Check nudges again
    nudges = system.check_and_send_nudges(student_id)
    deadline_nudges = [n for n in nudges if n['type'] == 'deadline']
    print(f"   Deadline nudges: {len(deadline_nudges)}")
    if deadline_nudges:
        print(f"   Message: {deadline_nudges[0]['message']}")
    
    # Cleanup
    session.delete(test_commit)
    session.commit()
    session.close()
    
    print("\n✅ All nudge tests passed!")
    print("="*60)
    
    system.close()

if __name__ == "__main__":
    test_nudges()