import sqlite3
import os

# Database path
db_path = '/data/monitor.db'

if not os.path.exists(db_path):
    # Connect to database (create if not exists)
    conn = sqlite3.connect(db_path)
    
    # Cursor to execute SQL
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS LOGS (
            session_id TEXT,
            app_name TEXT,
            type TEXT,
            message TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database {db_path} created.")
else:
    print(f"Database {db_path} already exists. Moving on.")
