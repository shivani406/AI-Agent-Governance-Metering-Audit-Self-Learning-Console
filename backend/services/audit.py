"""
writes and fetches audits
"""

from datetime import datetime
from database.connection import get_db_connection

def write_audit_entry(event_type: str, agent_name: str, actor: str, action: str, reason: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (timestamp, event_type, agent_name, actor, action, reason)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (datetime.utcnow().isoformat(), event_type, agent_name, actor, action, reason))
    conn.commit()
    conn.close()

def fetch_audit_entries():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT timestamp, event_type, agent_name, actor, action, reason FROM audit_logs ORDER BY id DESC")
    logs =[]
    for row in cursor.fetchall():
        logs.append(dict(row))

    conn.close()
    return logs