"""
Tracks usage of Agent to Agent calls
- Logs each call with details like caller, target, units consumed, cost, and status (allowed/blocked)
- Provides an endpoint to retrieve usage summaries for all agents
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from agent_governance_console.database.db_connection import get_db_connection
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
    caller_row = cursor.fetchone()
    cursor.execute("""
                    SELECT * FROM agents WHERE agent_name = ?
                   """, (payload.target,))
    target_row = cursor.fetchone()

    if not target_row or not caller_row:
        missing = payload.caller if not caller_row else payload.target
        raise HTTPException(status_code= 404, detail=f"Unknown Agent: {missing}")
    
    caller_agent = dict(caller_row)
    target_agent = dict(target_row)

    if caller_agent["status"] == "blocked" or target_agent["status"] == "blocked":
        add_telemetry_log(cursor, payload.request_id, payload.caller, payload.target, payload.units, payload.cost, "usage_rejected")
        db.commit()
        raise HTTPException(status_code=403, detail= f"Agent {payload.caller} is blocked from making calls")
    

@router.get("/usage-summary", status_code= 200)

#=========complete this (2 agents - caller + target) --> mapping their token usage ??

def get_usage_summary(db = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
                    SELECT agent_name, usage_count FROM agents
                   """)
    summary = [dict(row) for row in cursor.fetchall()]
    return {"summary": summary}

