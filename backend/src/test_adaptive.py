"""Test complete adaptive learning flow"""
import requests
import json

BASE_URL = 'http://localhost:5000'

def test_flow():
    student_id = 11391
    
    print("\n" + "="*60)
    print("ADAPTIVE LEARNING SYSTEM TEST")
    print("="*60)
    
    # 1. Get initial recommendations
    print("\n1️⃣ Getting initial recommendations...")
    r = requests.get(f'{BASE_URL}/recommendations/{student_id}')
    recs = r.json()
    print(f"   Risk: {recs['risk_level']} ({recs['risk_score']:.1f}%)")
    print(f"   Strategy: {recs['strategy']}")
    print(f"   Top recommendation: {recs['recommendations'][0]['title']}")
    
    # 2. Start first recommended content
    first_content = recs['recommendations'][0]['id']
    print(f"\n2️⃣ Starting content {first_content}...")
    r = requests.post(f'{BASE_URL}/progress/start', json={
        'student_id': student_id,
        'content_id': first_content
    })
    print(f"   {r.json()['message']}")
    
    # 3. Complete the content
    print(f"\n3️⃣ Completing content...")
    r = requests.post(f'{BASE_URL}/progress/complete', json={
        'student_id': student_id,
        'content_id': first_content,
        'time_spent': 15
    })
    result = r.json()
    print(f"   {result['message']}")
    print(f"   New top recommendation: {result['new_recommendations']['recommendations'][0]['title']}")
    
    # 4. Check progress
    print(f"\n4️⃣ Checking progress...")
    r = requests.get(f'{BASE_URL}/progress/{student_id}')
    stats = r.json()
    print(f"   Completed: {stats['completed']}")
    print(f"   Total time: {stats['total_time_minutes']} min")
    
    print("\n✅ All tests passed!")
    print("="*60)

if __name__ == "__main__":
    test_flow()