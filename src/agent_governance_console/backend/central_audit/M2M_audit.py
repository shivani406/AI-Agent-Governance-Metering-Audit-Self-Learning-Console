"""
This is a M2M (machine to machine) API - agent calls this to log their usage when they call other agents (caller + target + units consumed + cost + status)

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
    caller : int   # reffering agent by agent_id
    target : int
    caller_tokens: int
    target_tokens: int
    request_id : str
    
@router.post("/", status_code = 201)

def log_agent_to_agent_usage(payload : UsageRequest , db = Depends(get_db)):

    cursor = db.cursor()
    cursor.execute("""
                    SELECT * FROM agents WHERE agent_id = ?
                   """, (payload.caller,))
    caller_row = cursor.fetchone()
    cursor.execute("""
                    SELECT * FROM agents WHERE agent_id = ?
                   """, (payload.target,))
    target_row = cursor.fetchone()

    # if any of the agents involved in the call is missing
    if not target_row:
        add_security_incident_log (cursor, incident_type="missing_agent", description=f"Agent {payload.target} not found during usage logging for request {payload.request_id}",target_agent = payload.target)
        db.commit()
        raise HTTPException(status_code= 404, detail=f"Unknown Agent: {payload.target}")
    if not caller_row:
        add_security_incident_log (cursor, incident_type="missing_agent", description=f"Agent {payload.caller} not found during usage logging for request {payload.request_id}", caller_agent = payload.caller)
        db.commit()
        raise HTTPException(status_code= 404, detail=f"Unknown Agent: {payload.caller}")

    # if any of the agents involved in the call is blocked
    caller_agent = dict(caller_row)
    target_agent = dict(target_row)

    if target_agent["status"] == "blocked":
        add_security_incident_log (cursor, incident_type="blocked_agent_call", description=f"Agent {payload.target} is blocked",target_agent = payload.target)
        db.commit()
        raise HTTPException(status_code=403, detail= f"Agent {payload.target} is blocked from making calls")
        
    if caller_agent["status"] == "blocked":
        add_security_incident_log (cursor, incident_type="blocked_agent_call", description=f"Agent {payload.caller} is blocked", caller_agent = payload.caller)
        db.commit()
        raise HTTPException(status_code=403, detail= f"Agent {payload.caller} is blocked from making calls")
        
    
    # if all the request is clear,(no missing or blocked agents) then log the usage in usage_ledger 
    
    add_usage_ledger(cursor, request_id= payload.request_id, caller_agent= payload.caller, target_agent= payload.target, caller_tokens_consumed= payload.caller_tokens, target_tokens_consumed= payload.target_tokens)
    db.commit()
    cursor.execute("""
                    UPDATE agents
                   SET usage_count = usage_count + 1
                   WHERE agent_id IN (?, ?)
                   """, (payload.caller, payload.target)
                   )
    cursor.execute("""
                    UPDATE agents
                     SET tokens_consumed = tokens_consumed + ?
                     WHERE agent_id = ?
                     """, (payload.caller_tokens, payload.caller)
                     )
    cursor.execute("""
                    UPDATE agents
                     SET tokens_consumed = tokens_consumed + ?
                     WHERE agent_id = ?
                     """, (payload.target_tokens, payload.target)
                     )

    db.commit()
    return {"status": "success", "message": "M2M Telemetry successfully recorded"}