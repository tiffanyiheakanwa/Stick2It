import sqlite3
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "..", "procrastination.db")

def migrate():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Adding the fcm_token column to the student table
        cursor.execute("ALTER TABLE students ADD COLUMN fcm_token TEXT;")
        
        conn.commit()
        print(" Database updated: fcm_token column added.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e):
            print(" fcm_token already exists.")
        else:
            print(f" Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    migrate()