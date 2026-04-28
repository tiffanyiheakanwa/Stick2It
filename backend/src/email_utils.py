import os
from dotenv import load_dotenv
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from backend.src.logger import logger

# Load environment variables
env_path = 'sendgrid.env'
if os.path.exists(env_path):
    load_dotenv(os.path.join(os.getcwd(), env_path))
else:
    print(f"Warning: {env_path} not found. Ensure environment variables are set manually.")

def send_sendgrid_email(to_email, subject, body, user_name="Student"):
    """
    Core delivery logic for SendGrid.
    """
    # 1. Prepare the Mail object
    sg_mail = Mail(
        from_email=os.environ.get('SENDER_EMAIL', 'test@example.com'),
        to_emails=to_email,
        subject=subject,
        plain_text_content=body
    )
   
    try:
        # 2. Initialize the client with your API Key
        api_key = os.environ.get('SENDGRID_API_KEY')
        if not api_key:
            logger.warning(f"Simulating email to {to_email}: {body}")
            return True
            
        sg = SendGridAPIClient(api_key)
        response = sg.send(sg_mail)
        
        logger.info(f"SendGrid API Response: {response.status_code}")
        print(f"Email sent to {to_email}. Status Code: {response.status_code}")
        
        # SendGrid returns 200, 201, or 202 on success
        return response.status_code in [200, 201, 202]

    except Exception as e:
        logger.error(f"SendGrid Network Error: {e}")
        return False
