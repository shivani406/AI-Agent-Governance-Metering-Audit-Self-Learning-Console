""""
Handles the subroutines (agents) to be later used in main.py
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Literal
from agent_governance_console.database.db_connection import get_db_connection


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
        db.close() 

# Fetch all the agent data from agents table 
@router.get("/")
def get_all_agents( db = Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
                    SELECT * FROM AGENTS
                   """)
    agents = [dict(row) for row in cursor.fetchall()]
    return {"agents" : agents}

# change the agents permission (allow/block any agent)
@router.post("/{name}/decision", status_code = 201)
def change_agent_decision(name : str, payload : DecisionRequest, db = Depends(get_db)):
    
    cursor = db.cursor()
    cursor.execute("""
                    SELECT * FROM agents WHERE agent_name = ?
                   """ , (name,)
                   )
    agent = cursor.fetchone()
    if not agent:
         
         raise HTTPException (status_code= 404, detail= "Agent not Found")
    # log agent not found in security incident logs

    if agent["risk_level"] == "high" and payload.decision == "allowed" and not payload.reason.strip() :
        raise HTTPException(status_code=400, detail="High Risk Agents require a reason to be allowed")
    # log calling blocked agent in security incident logs
    cursor.execute("""
                    UPDATE agents
                    SET status = ? , last_decision_reason = ?
                    WHERE agent_name = ?
                    """ ,(payload.decision, payload.reason, name)
                    )
    #== decide where to log the agent permission changes in which log table??
    db.commit()
    return {"message" : f"Agent {name} updated successfully !"}



    
    