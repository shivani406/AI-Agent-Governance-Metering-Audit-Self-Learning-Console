""""
Handles the subroutines (agents) to be later used in main.py
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
from agent_governance_console.database.connection import get_db_connection
from agent_governance_console.backend.services.audit import add_audit_log

router = APIRouter()

class DecisionRequest(BaseModel):
    
    decision : Literal["allowed" , "blocked" , "pending_review"]
    reason : str
    approved_by : str

def get_db():
    db = get_db_connection()
    try:
        yield db  # to keep the connection open until query is executed
    finally:
        db.close() # safety net to close DB if request stops in between

# use router to navigate 
@router.get("/")
def get_all_agents( db = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
                    SELECT * FROM AGENTS
                   """)
    agents = cursor.fetchall()
    return {"agents" : agents}

@router.post("/{name}/decision", status_code = 201)
def create_agent_decision(name : str, payload : DecisionRequest, db = Depends(get_db)):
    
    cursor = db.cursor()
    cursor.execute("""
                    SELECT * FROM agents WHERE agent_name = ?
                   """ , (name,)
                   )
    agent = cursor.fetchone()
    if not agent:
         raise HTTPException (status_code= 404, detail= "Agent not Found")
    
    if agent["risk_level"] == "high" and payload.decision == "allowed" and not payload.reason.strip() :
        raise HTTPException(status_code=400, detail="High Risk Agents require a reason to be allowed")
    
    cursor.execute("""
                    UPDATE agents
                    SET status = ? , last_decision_reason = ?
                    WHERE agent_name = ?
                    """ ,(payload.decision, payload.reason, name)
                    )
    # generate corressponding audit log
    add_audit_log(cursor, agent["agent_id"], payload.decision, 0, payload.approved_by, policy_id=None)

    db.commit()
    return {"message" : f"Agent {name} updated successfully !"}

@router.get("/debug/{name}")
def debug_agent_data(name: str, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM agents WHERE agent_name = ?", (name,))
    row = cursor.fetchone()
    if not row:
        return {"error": "Agent not found in database"}
    return {"database_values": dict(row)}

    
    