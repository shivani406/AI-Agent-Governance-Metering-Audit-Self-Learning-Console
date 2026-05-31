""""
Handles the subroutines (agents) to be later used in main.py
"""
from fastapi import APIRouter, Depends
from agent_governance_console.database.connection import get_db_connection

router = APIRouter()

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

