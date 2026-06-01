"""
Tracks usage of Agent to Agent calls
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from agent_governance_console.database.connection import get_db_connection
from agent_governance_console.backend.services.audit import add_audit_log

router = APIRouter()

class UsageRequest(BaseModel):
    caller : str
    target : str
    units : int
    cost : float
    request_id : str

def get_db():
    db = get_db_connection()
    try : 
        yield db
    finally : 
        db.close()

@router.post("/", status_code = 201)
def log_usage(payload : UsageRequest , db = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
                    SELECT * FROM agents WHERE agent_name = ?
                   """, (payload.caller,))
    row = cursor.fetchone()
    if not row:
        add_audit_log(cursor, 0, "usage_rejected", payload.units, payload.caller, None )
