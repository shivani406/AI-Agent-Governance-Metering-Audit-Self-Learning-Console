import os
import sqlite3

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if os.path.basename(current_dir) == "database":
    BASE_DIR = parent_dir
else:
    BASE_DIR = current_dir
DB_PATH = os.path.join(BASE_DIR, "governance.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn