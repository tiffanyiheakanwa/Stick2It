import sqlite3

def run():
    conn = sqlite3.connect('backend/procrastination.db')
    c = conn.cursor()
    try:
        c.execute('ALTER TABLE assignments ADD COLUMN source_platform VARCHAR(50) DEFAULT "local"')
        c.execute('ALTER TABLE assignments ADD COLUMN external_id VARCHAR(255)')
        conn.commit()
        print("Migrated successfully")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    run()
