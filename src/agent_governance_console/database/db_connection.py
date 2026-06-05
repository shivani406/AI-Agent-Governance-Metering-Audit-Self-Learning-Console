import pathlib
import sqlite3

# path where my database will reside
DB_PATH = pathlib.Path(__file__).resolve().parent.parent.parent.parent / "governance.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
