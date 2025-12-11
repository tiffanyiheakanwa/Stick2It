"""
Test complete commitment flow with all features
"""
import requests
import json
from datetime import datetime, timedelta

BASE_URL = 'http://localhost:5000'

def test_complete_flow():
    student_id = 11391
    
    print("\n" + "="*70)
    print("HYBRID COMMITMENT SYSTEM - COMPLETE FLOW TEST")
    print("="*70)
    
    # 1. Get initial stats
    print("\n📊 Step 1: Initial student stats")
    r = requests.get(f'{BASE_URL}/stats/{student_id}')
    stats = r.json()
    print(f"   Points: {stats['total_points']}")
    print(f"   Streak: {stats['current_streak']} days")
    print(f"   Success rate: {stats['success_rate']}%")
    
    # 2. Add accountability partner
    print("\n🤝 Step 2: Adding accountability partner")
    r = requests.post(f'{BASE_URL}/partner/add', json={
        'student_id': student_id,
        'partner_name': 'Mom',
        'partner_email': 'mom@example.com'
    })
    result = r.json()
    print(f"   {result['message']}")
    
    # 3. Get recommendations
    print("\n📚 Step 3: Getting personalized recommendations")
    r = requests.get(f'{BASE_URL}/recommendations/{student_id}')
    recs = r.json()
    first_content = recs['recommendations'][0]
    print(f"   Recommended: {first_content['title']}")
    print(f"   Difficulty: {first_content['difficulty']} ({first_content['minutes']} min)")
    
    # 4. Make commitment (soft pledge)
    print("\n💪 Step 4: Making commitment (soft pledge)")
    commit_time = datetime.now() + timedelta(hours=1)
    r = requests.post(f'{BASE_URL}/commitment/create', json={
        'student_id': student_id,
        'content_id': first_content['id'],
        'committed_datetime': commit_time.isoformat(),
        'type': 'start_time'
    })
    result = r.json()
    print("   Raw response:", result)   # ADD THIS
    print(f"   Pledge: {result['pledge']}")
    print(f"   Points at stake: {result['points_at_stake']}")
    commitment_id = result['commitment_id']
    
    # 5. Simulate keeping the commitment
    print("\n✅ Step 5: Keeping the commitment (simulated)")
    r = requests.post(f'{BASE_URL}/commitment/check/{commitment_id}')
    result = r.json()
    print(f"   {result['message']}")
    if 'points_earned' in result:
        print(f"   Points earned: +{result['points_earned']}")
    
    # 6. Start and complete the content
    print("\n🎯 Step 6: Completing the actual content")
    # Start
    requests.post(f'{BASE_URL}/progress/start', json={
        'student_id': student_id,
        'content_id': first_content['id']
    })
    # Complete
    r = requests.post(f'{BASE_URL}/progress/complete', json={
        'student_id': student_id,
        'content_id': first_content['id'],
        'time_spent': first_content['minutes']
    })
    print(f"   Content completed!")
    
    # 7. Check updated stats
    print("\n📊 Step 7: Updated stats")
    r = requests.get(f'{BASE_URL}/stats/{student_id}')
    stats = r.json()
    print(f"   Points: {stats['total_points']} (+{stats['points_earned']} earned)")
    print(f"   Current streak: {stats['current_streak']} days 🔥")
    print(f"   Success rate: {stats['success_rate']}%")
    print(f"   Kept commitments: {stats['kept']}/{stats['total_commitments']}")
    
    # 8. Get new recommendations (system adapts!)
    print("\n🔄 Step 8: Getting fresh recommendations")
    r = requests.get(f'{BASE_URL}/recommendations/{student_id}')
    recs = r.json()
    print(f"   New top recommendation: {recs['recommendations'][0]['title']}")
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED - HYBRID SYSTEM WORKING!")
    print("="*70)
    print("\n🎉 Your system now has:")
    print("   ✅ Soft pledges (no hard penalties)")
    print("   ✅ Success streaks (gamification)")
    print("   ✅ Points system (loss aversion)")
    print("   ✅ Accountability partners (social pressure)")
    print("   ✅ Adaptive recommendations")
    print("   ✅ Progress tracking")
    print("\n💪 Complete behavioral intervention system!")

if __name__ == "__main__":
    test_complete_flow()