"""
Tracks usage of Agent to Agent calls
- POST /usage is an Ingestion & Policy Enforcement Gateway.
- This is the main the data input pipeline for our entire metering ecosystem.
- Logs each call with details like caller, target, units consumed, cost, and status (allowed/blocked)
- Provides an endpoint to retrieve usage summaries for all agents
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from agent_governance_console.database.db_connection import get_db_connection

router = APIRouter()

class UsageRequest(BaseModel):
    caller : str
    target : str
    caller_tokens: int
    target_tokens: int
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

        db.commit()
        raise HTTPException(status_code=403, detail= f"Agent {payload.caller} is blocked from making calls")
    

@router.get("/usage-summary", status_code= 200)

#========= add the usage summary from the usage_ledger

def get_usage_summary(db = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
                    SELECT agent_name, usage_count FROM agents
                   """)
    summary = [dict(row) for row in cursor.fetchall()]
    return {"summary": summary}

