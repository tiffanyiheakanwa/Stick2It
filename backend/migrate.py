import sqlite3
conn = sqlite3.connect('backend/procrastination.db')
c = conn.cursor()
try:
    c.execute('ALTER TABLE students ADD COLUMN auth_provider VARCHAR(50) DEFAULT "local"')
    c.execute('ALTER TABLE students ADD COLUMN ext_access_token VARCHAR')
    c.execute('ALTER TABLE students ADD COLUMN ext_refresh_token VARCHAR')
    c.execute('ALTER TABLE students ADD COLUMN ext_token_expires_at DATETIME')
except Exception as e:
    print(e)
conn.commit()
conn.close()
print("Migrated successfully")
