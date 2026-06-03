""""
Handles the subroutines (agents) to be later used in main.py
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
from agent_governance_console.database.db_connection import get_db_connection
from agent_governance_console.backend.services.audit import add_governance_log

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
    agents = [dict(row) for row in cursor.fetchall()]
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
    action_string = f"agent_{payload.decision}"
    add_governance_log(cursor, agent["agent_id"], action_string, payload.approved_by, payload.reason)

    db.commit()
    return {"message" : f"Agent {name} updated successfully !"}



    
    