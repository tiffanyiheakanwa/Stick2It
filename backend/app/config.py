import os
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv

# Load variables from the .env file in the project root
load_dotenv()

# Load the secret from environment variables
SECRET_KEY = os.getenv("STICK2IT_SECRET_KEY", "fallback-dev-key")
SECURITY_SALT = "buddy-verification-salt"

# Initialize the serializer once for the app
serializer = URLSafeTimedSerializer(SECRET_KEY)