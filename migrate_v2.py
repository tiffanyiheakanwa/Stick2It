import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'backend', 'app', 'procrastination.db')
# If the above doesn't exist, try the backend root
if not os.path.exists(db_path):
    db_path = os.path.join(os.path.dirname(__file__), 'procrastination.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE students ADD COLUMN grace_period_lenience FLOAT DEFAULT 1.0;")
    print("Added grace_period_lenience column.")
except sqlite3.OperationalError as e:
    print(f"grace_period_lenience might already exist: {e}")

try:
    cursor.execute("ALTER TABLE student_progress ADD COLUMN time_spent INTEGER DEFAULT 0;")
    print("Added time_spent column to student_progress.")
except sqlite3.OperationalError as e:
    print(f"time_spent might already exist: {e}")

conn.commit()
conn.close()
