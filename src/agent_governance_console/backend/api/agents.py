""""
Handles the subroutines (agents) to be later used in main.py
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
from agent_governance_console.database.db_connection import get_db_connection
from agent_governance_console.backend.central_audit.insert_logs_into_schema import add_security_incident_log
from agent_governance_console.backend.central_audit.insert_logs_into_schema import add_governance_log

router = APIRouter()

class DecisionRequest(BaseModel):
    
    agent_id : int
    decision : Literal["allowed" , "blocked" , "pending_review"]
    reason : str
    approved_by : str

def get_db():
    db = get_db_connection()
    try:
        yield db  # to keep the connection open until query is executed
    finally:
        db.close() 


@router.get("/")
def get_all_agents( db = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
                    SELECT * FROM AGENTS
                   """)
    agents = [dict(row) for row in cursor.fetchall()]
    return {"agents" : agents}

# change the agents permission (allow/block any agent)
@router.post("/{agent_id}/decision", status_code = 201)
def change_agent_decision(agent_id : int, payload : DecisionRequest, db = Depends(get_db)):
    
    cursor = db.cursor()
    cursor.execute("""
                    SELECT * FROM agents WHERE agent_id = ?
                   """ , (agent_id,))
    agent = cursor.fetchone()
    if not agent:
        add_security_incident_log(cursor, incident_type="missing_agent", description=f"Agent {agent_id} not found during decision making")
        raise HTTPException (status_code= 404, detail= "Agent not Found")
   

    if agent["risk_level"] == "high" and payload.decision == "allowed" and not payload.reason.strip() :
        add_security_incident_log(cursor, incident_type="high_risk_agent", description=f"High risk agent {agent_id} was allowed without a reason")
        raise HTTPException(status_code=400, detail="High Risk Agents require a reason to be allowed")
    
    cursor.execute("""
                    UPDATE agents
                    SET status = ? , last_decision_reason = ?
                    WHERE agent_id = ?
                    """ ,(payload.decision, payload.reason, agent_id)
                    )
   
    add_governance_log(cursor, agent_id=agent_id, decision=payload.decision, reason=payload.reason, approved_by=payload.approved_by)
    db.commit()
    return {"message" : f"Agent {agent_id} updated successfully !"}



    
    