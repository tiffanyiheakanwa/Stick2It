"""Test the smart local fallback without calling the Gemini API."""
import sys
sys.path.insert(0, '.')

from backend.src.task_ai import _smart_mock

test_cases = [
    ("CSC 446 ASSIGNMENT", "Distributed systems coursework"),
    ("Write essay on climate change", None),
    ("Build a React dashboard project", None),
    ("Study for calculus exam", None),
    ("Prepare presentation on machine learning", None),
    ("Read Chapter 5 of the textbook", None),
]

for title, desc in test_cases:
    print(f"\n{'='*55}")
    print(f"Task: {title}")
    subtasks = _smart_mock(title, desc)
    for i, s in enumerate(subtasks, 1):
        print(f"  {i}. [{s['estimated_minutes']} min] {s['title']}")
