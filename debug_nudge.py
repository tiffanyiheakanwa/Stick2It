import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.src.nudge_system import SmartNudgeSystem
import logging

logging.basicConfig(level=logging.DEBUG)

ns = SmartNudgeSystem()
nudges = ns.check_and_send_nudges(1)

print(f"Nudges returned: {nudges}")
