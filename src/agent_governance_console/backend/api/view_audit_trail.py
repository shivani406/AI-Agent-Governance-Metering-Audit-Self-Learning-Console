"""
View the Audit logs from all the three tables in a single endpoint
"""

from fastapi import APIRouter, Depends

from agent_governance_console.database.db_connection import get_db_connection

router = APIRouter()


def get_db():
    db = get_db_connection()
    try:
        yield db
    finally:
        db.close()


@router.get("/", status_code=200)
def get_audit_trail(db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM governance_logs ORDER BY timestamp DESC")
    governance = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM usage_ledger ORDER BY timestamp DESC")
    usage = [dict(row) for row in cursor.fetchall()]
    cursor.execute("SELECT * FROM security_incident_logs ORDER BY timestamp DESC")
    security = [dict(row) for row in cursor.fetchall()]
    return {
        "governance_logs": governance,
        "usage_ledger": usage,
        "security_incident_logs": security,
    }
