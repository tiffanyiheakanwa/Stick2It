"""
SendGrid Diagnostic Script
Run from the project root: python backend/scripts/check_sendgrid.py
"""
import os
import sys

# Ensure project root is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from dotenv import load_dotenv

print("=" * 60)
print("SENDGRID DIAGNOSTIC")
print("=" * 60)

# 1. Check CWD
cwd = os.getcwd()
print(f"\n[1] CWD: {cwd}")

# 2. Look for .env / sendgrid.env in several places
candidates = [
    os.path.join(cwd, 'sendgrid.env'),
    os.path.join(cwd, '.env'),
    os.path.join(cwd, 'backend', 'sendgrid.env'),
    os.path.join(cwd, 'backend', '.env'),
]
loaded_from = None
for path in candidates:
    if os.path.exists(path):
        load_dotenv(path, override=False)
        print(f"[2] Loaded env from: {path}")
        loaded_from = path
        break

if not loaded_from:
    print("[2] WARNING: No sendgrid.env or .env file found in any expected location!")
    print("    Searched:", candidates)

# 3. Check keys
api_key = os.environ.get('SENDGRID_API_KEY', '')
sender  = os.environ.get('SENDER_EMAIL', '')

print(f"\n[3] SENDGRID_API_KEY : {'SET -> ' + api_key[:10] + '...' if api_key else 'NOT SET'}")
print(f"[3] SENDER_EMAIL     : {sender if sender else 'NOT SET'}")

if not api_key:
    print("\n[!] SENDGRID_API_KEY is missing — emails will only be simulated (logged).")
    print("    Fix: add SENDGRID_API_KEY=SG.xxx to your sendgrid.env file.")
    sys.exit(1)

if not sender:
    print("\n[!] SENDER_EMAIL is missing — SendGrid requires a verified sender address.")
    print("    Fix: add SENDER_EMAIL=noreply@yourdomain.com to your sendgrid.env file.")
    sys.exit(1)

# 4. Attempt a real test send
print("\n[4] Attempting test email via SendGrid API...")
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

TO_EMAIL = sender  # send to yourself as a sanity check

msg = Mail(
    from_email=sender,
    to_emails=TO_EMAIL,
    subject="[Stick2It] SendGrid Diagnostic Test",
    plain_text_content="This is a test email from the Stick2It diagnostic script. If you see this, SendGrid is working!"
)

try:
    sg = SendGridAPIClient(api_key)
    response = sg.send(msg)
    print(f"[4] SendGrid response status: {response.status_code}")
    if response.status_code in [200, 201, 202]:
        print(f"    SUCCESS — email dispatched to {TO_EMAIL}")
    else:
        print(f"    UNEXPECTED STATUS — body: {response.body}")
except Exception as e:
    print(f"[4] ERROR: {e}")
    # Print full error details for SendGrid HTTP errors
    if hasattr(e, 'body'):
        print(f"    Response body: {e.body}")
    if hasattr(e, 'status_code'):
        print(f"    Status code: {e.status_code}")
    sys.exit(1)

print("\n[5] Checking email_utils.py load path...")
try:
    from backend.src.email_utils import send_sendgrid_email
    print("    email_utils imported OK")
    # The env is already loaded above, so this should work
    result = send_sendgrid_email(TO_EMAIL, "[Stick2It] email_utils test", "email_utils wrapper test", "Diagnostic")
    print(f"    send_sendgrid_email returned: {result}")
except Exception as e:
    print(f"    email_utils error: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
