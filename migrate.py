import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'procrastination.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    cursor.execute("ALTER TABLE students ADD COLUMN experimental_group BOOLEAN DEFAULT 0;")
    print("Added experimental_group column.")
except sqlite3.OperationalError as e:
    print(f"Column might already exist: {e}")

conn.commit()
conn.close()
