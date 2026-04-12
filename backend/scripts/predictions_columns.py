import sqlite3
import os

def migrate_predictions():
    # 1. Smarter Path Logic
    # This finds the 'Stick2It' root folder by looking for the 'backend' directory
    current_path = os.getcwd()
    if "scripts" in current_path:
        db_path = os.path.join("..", "procrastination.db")
    else:
        db_path = os.path.join("backend", "procrastination.db")

    conn = None # Initialize so 'finally' doesn't crash
    try:
        if not os.path.exists(db_path):
            print(f"❌ Error: Database not found at {os.path.abspath(db_path)}")
            return

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print(f"Connected to {db_path}. Adding columns...")
        
        # Add columns one by one
        try:
            cursor.execute("ALTER TABLE predictions ADD COLUMN actual_outcome INTEGER;")
        except sqlite3.OperationalError:
            print("ℹ️ actual_outcome already exists.")

        try:
            cursor.execute("ALTER TABLE predictions ADD COLUMN feedback_received_at DATETIME;")
        except sqlite3.OperationalError:
            print("ℹ️ feedback_received_at already exists.")
        
        conn.commit()
        print("✅ Success: Prediction table is now ready for Phase 4.")

    except Exception as e:
        print(f"❌ Migration failed: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    migrate_predictions()