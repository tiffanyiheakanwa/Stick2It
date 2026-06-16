import os
import sys
sys.path.insert(0, '.')

from dotenv import load_dotenv
load_dotenv('sendgrid.env', override=True)

from backend.src.email_utils import send_sendgrid_email

# Sending TO iheakanwa.tiffany@gmail.com (the app's registered email)
# SMTP will send FROM tiffanyiheakanwa@gmail.com (where App Password was generated)
to_email = 'iheakanwa.tiffany@gmail.com'
subject  = 'Action Required: CSC 446 ASSIGNMENT is due soon!'
body     = (
    "Hey Tiffany! Your deadline for CSC 446 ASSIGNMENT is approaching. "
    "You have points on the line - don't let your streak reset to 0. "
    "Log in now and mark your progress before the deadline hits!"
)

print(f"Sending test nudge to {to_email}...")
result = send_sendgrid_email(to_email, subject, body, user_name="Tiffany")

if result:
    print("SUCCESS - Email sent! Check your inbox at iheakanwa.tiffany@gmail.com")
else:
    print("FAILED - check the logs above for details.")
