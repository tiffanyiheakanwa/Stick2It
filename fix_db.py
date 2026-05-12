import sqlite3
import os

def migrate_everything():
    found_any = False
    # Required columns based on your "RemindAI" model errors
    required_columns = [
        ("experimental_group", "BOOLEAN DEFAULT FALSE"),
        ("grace_period_lenience", "INTEGER DEFAULT 0"),
        ("fcm_token", "TEXT"),
        ("auth_provider", "TEXT"),
        ("ext_access_token", "TEXT"),
        ("ext_refresh_token", "TEXT"),
        ("ext_token_expires_at", "DATETIME")
    ]

    print("--- Searching for database files... ---")
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".db"):
                found_any = True
                db_path = os.path.join(root, file)
                print(f"\nProcessing: {db_path}")
                
                try:
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    
                    # Check if 'students' table exists
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='students';")
                    if not cursor.fetchone():
                        print(f"  - No 'students' table found in {file}. Skipping.")
                        continue
                    
                    # Check current columns
                    cursor.execute("PRAGMA table_info(students);")
                    existing_cols = [col[1] for col in cursor.fetchall()]
                    
                    for col_name, col_type in required_columns:
                        if col_name not in existing_cols:
                            cursor.execute(f"ALTER TABLE students ADD COLUMN {col_name} {col_type};")
                            print(f"  + Added column: {col_name}")
                        else:
                            print(f"  . Column {col_name} already exists.")
                    
                    conn.commit()
                    conn.close()
                    print(f"--- Finished {file} ---")
                except Exception as e:
                    print(f"  ! Error: {e}")

    if not found_any:
        print("--- No .db files found in this directory or subdirectories! ---")

if __name__ == "__main__":
    migrate_everything()