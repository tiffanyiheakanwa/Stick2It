import sqlite3
import os

# Path to your database
db_path = os.path.join("backend", "procrastination.db")

def migrate():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Connecting to {db_path}...")
        
        # Add the missing column
        cursor.execute("ALTER TABLE nudges ADD COLUMN commitment_id INTEGER;")
        
        conn.commit()
        print("Success! 'commitment_id' column added to 'nudges' table.")
        
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column already exists. No action needed.")
        else:
            print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate()