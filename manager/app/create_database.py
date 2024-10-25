import sqlite3
import os

# Database path
db_path = '/data/monitor.db'

if not os.path.exists(db_path):
    # Connect to database (create if not exists)
    conn = sqlite3.connect(db_path)
    conn.close()
    print(f"Database {db_path} created.")
else:
    print(f"Database {db_path} already exists. Moving on.")
