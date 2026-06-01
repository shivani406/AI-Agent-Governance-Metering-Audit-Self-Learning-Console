from fastapi import APIRouter, Depends
from agent_governance_console.database.connection import get_db_connection

router = APIRouter()

def get_db():
    db = get_db_connection()
    try:
        yield db
    finally:
        db.close()

@router.get("/" , status_code= 200)
def  get_audit_trail(db = Depends(get_db)):
    cursor = db.cursor
    cursor.execute("""
        SELECT 
            g.timestamp,
            g.action_taken AS event_type,
            a.agent_name,
            g.action_taken AS action,
            g.approved_by AS actor,
            g.reason
        FROM governance_audit_logs g
        LEFT JOIN agents a ON g.agent_id = a.agent_id
        
        UNION ALL
        
        SELECT 
            t.timestamp,
            t.status AS event_type,
            t.caller_agent_name AS agent_name,
            'units: ' || t.units_consumed || ', cost: ' || t.cost AS action,
            'system' AS actor,
            'Request ID: ' || t.request_id AS reason
        FROM usage_telemetry t
        
        ORDER BY timestamp DESC
    """)

    #== to return logs for a entered time period by the user
    logs = [dict(row) for row in cursor.fetchall()]
    return {"audit_logs" : logs}