import sys
import os
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.email_utils import send_sendgrid_email
from backend.src.nudge_system import SmartNudgeSystem

# Load env to ensure SendGrid keys are available
load_dotenv('sendgrid.env')

def test_sendgrid():
    api_key = os.environ.get("SENDGRID_API_KEY")
    if not api_key or "dummy" in api_key.lower() or "your_" in api_key.lower():
        print("SendGrid API key not set or is still dummy. Skipping real email test.")
        return False
        
    print("Testing SendGrid...")
    try:
        # We don't have a real target email, so we just check if it fails or succeeds
        # Sending to a placeholder to see if the SendGrid client accepts it
        success = send_sendgrid_email(
            to_email="test@example.com", 
            subject="RemindAI Test Email", 
            body="This is a test to verify SendGrid is configured correctly."
        )
        print(f"SendGrid result: {success}")
        return success
    except Exception as e:
        print(f"SendGrid error: {e}")
        return False

def test_firebase():
    print("Testing Firebase initialization...")
    try:
        ns = SmartNudgeSystem()
        # This will fail if firebase-adminsdk.json is invalid or not authenticated
        # We don't have a real device token to send to, so we just attempt a dummy send
        # It should fail with an auth/token error, but NOT a missing credentials error
        print("Firebase is initialized. Attempting a dummy push...")
        
        # This will likely return False or throw because 'dummy_token' is invalid,
        # but if it throws an authentication error, it means the service account is invalid.
        result = ns._send_firebase_push("dummy_token", "Test", "Test body")
        print(f"Firebase push result: {result}")
        return True
    except Exception as e:
        print(f"Firebase error: {e}")
        return False

if __name__ == "__main__":
    print("--- RemindAI Notification Test ---")
    
    sg_ok = test_sendgrid()
    fb_ok = test_firebase()
    
    print("\n--- Results ---")
    print(f"SendGrid: {'SUCCESS' if sg_ok else 'FAILED/SKIPPED'}")
    print(f"Firebase Config: {'SUCCESS' if fb_ok else 'FAILED'}")
