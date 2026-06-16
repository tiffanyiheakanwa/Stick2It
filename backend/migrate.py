import sqlite3
conn = sqlite3.connect('backend/procrastination.db')
c = conn.cursor()

try:
    c.execute('ALTER TABLE students ADD COLUMN auth_provider VARCHAR(50) DEFAULT "local"')
    c.execute('ALTER TABLE students ADD COLUMN ext_access_token VARCHAR')
    c.execute('ALTER TABLE students ADD COLUMN ext_refresh_token VARCHAR')
    c.execute('ALTER TABLE students ADD COLUMN ext_token_expires_at DATETIME')
except Exception as e:
    print(f"Skipping student columns: {e}")

try:
    c.execute('ALTER TABLE nudges ADD COLUMN reaction_time FLOAT')
    print("Added reaction_time to nudges")
except Exception as e:
    print(f"Skipping reaction_time: {e}")

try:
    c.execute('ALTER TABLE nudges ADD COLUMN is_successful_conversion BOOLEAN DEFAULT 0')
    print("Added is_successful_conversion to nudges")
except Exception as e:
    print(f"Skipping is_successful_conversion: {e}")

try:
    c.execute('ALTER TABLE student_progress ADD COLUMN time_spent INTEGER DEFAULT 0')
    print("Added time_spent to student_progress")
except Exception as e:
    print(f"Skipping time_spent: {e}")

conn.commit()
conn.close()
print("Migrated successfully")
