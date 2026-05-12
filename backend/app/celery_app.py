import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()

# Initialize Celery
# Redis URL defaults to localhost; in production (Render), this will be an env var
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "RemindAI",
    broker=REDIS_URL,
    backend=REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    # This ensures tasks don't get lost if a worker crashes
    task_acks_late=True, 
)