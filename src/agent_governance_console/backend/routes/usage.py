"""
Tracks usage of Agent to Agent calls
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from agent_governance_console.database.connection import get_db_connection
from agent_governance_console.backend.services.audit import add_telemetry_log

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
        add_telemetry_log(cursor, payload.request_id, payload.caller, payload.target, payload.units, payload.cost, "usage_rejected")
        db.commit()
        raise HTTPException(status_code= 404, detail= f"Unknown Agent : {payload.caller}")
    
    agent = dict(row)
    if agent["status"] == "blocked":
        add_telemetry_log(cursor, payload.request_id, payload.caller, payload.target, payload.units, payload.cost, "usage_rejected")
        db.commit()
        raise HTTPException(status_code=403, detail= f"Agent {payload.caller} is blocked from making calls")
    

@router.get("/usage-summary", status_code= 200)
def get_usage_summary(db = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
                    SELECT agent_name, usage_count FROM agents
                   """)
    summary = [dict(row) for row in cursor.fetchall()]
    return {"summary": summary}

