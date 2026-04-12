import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "..", "procrastination.db")

def add_column():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Connecting to {db_path}...")
        
        # Add fcm_token to the students table
        cursor.execute("ALTER TABLE students ADD COLUMN fcm_token TEXT;")
        
        conn.commit()
        print(" Success: 'fcm_token' column added to 'students' table.")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print(" Column already exists. Skipping.")
        else:
            print(f" Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    add_column()