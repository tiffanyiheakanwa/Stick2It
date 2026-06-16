import os, sys
sys.path.insert(0, '.')
from dotenv import load_dotenv
load_dotenv('.env', override=True)

from backend.app.config import GEMINI_API_KEY
from backend.src.task_ai import task_ai_service
import traceback

print(f"Gemini key present: {bool(GEMINI_API_KEY)}")
if GEMINI_API_KEY:
    print(f"Key preview: {GEMINI_API_KEY[:12]}...")

print("\nTesting breakdown for: CSC 446 ASSIGNMENT")
print("-" * 50)

try:
    result = task_ai_service.breakdown_task(
        title="CSC 446 ASSIGNMENT",
        description="Complete the CSC 446 assignment on distributed systems",
    )
    print(f"Got {len(result)} subtasks:")
    for i, s in enumerate(result, 1):
        mins = s.get("estimated_minutes", "?")
        print(f"  {i}. [{mins} min] {s['title']}")
except Exception as e:
    print("ERROR:")
    traceback.print_exc()
