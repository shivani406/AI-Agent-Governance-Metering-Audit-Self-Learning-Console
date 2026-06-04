"""
This is a (M2M) API - agent calls this to log their usage when they call other agents (caller + target + units consumed + cost + status)

Handles Audit generation and SHA-256 hashing for tamper-proof logging
- contains all the functions required to log
    - the agent permission changes 
    - usage telemetry 
    - security incidents (like calling blocked agents, missing agents, etc.)
- implements hash chaining for data integrity

"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from agent_governance_console.database.db_connection import get_db_connection
from agent_governance_console.backend.central_audit.insert_logs_into_schema import add_usage_ledger, add_security_incident_log

router = APIRouter()

def get_db():
    db = get_db_connection()
    try : 
        yield db
    finally : 
        db.close()

class UsageRequest(BaseModel):
    caller : str
    target : str
    caller_tokens: int
    target_tokens: int
    request_id : str
    
@router.post("/", status_code = 201)

def log_agent_to_agent_usage(payload : UsageRequest , db = Depends(get_db)):

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
        # log an incident for missing agent in security incident logs
        raise HTTPException(status_code= 404, detail=f"Unknown Agent: {missing}")

    caller_agent = dict(caller_row)
    target_agent = dict(target_row)

    if caller_agent["status"] == "blocked" or target_agent["status"] == "blocked":
        # log calling blocked agent in security incident logs
        raise HTTPException(status_code=403, detail= f"Agent {payload.caller} is blocked from making calls")
    
    # if all the request is clear,(no missing or blocked agents) then log the usage in usage_ledger for both caller and target agents with the respective tokens consumed
    # also update the usage count in agents table for both caller and target agents

