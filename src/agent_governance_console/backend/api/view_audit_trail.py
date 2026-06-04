"""
View the three log tables in the frontend in a tabular format with filters for time period, agent name, etc.
"""
from fastapi import APIRouter, Depends
from agent_governance_console.database.db_connection import get_db_connection

router = APIRouter()

def get_db():
    db = get_db_connection()
    try:
        yield db
    finally:
        db.close()

@router.get("/" , status_code= 200)


# give 3 endpoints to view all the 3 audit tables data in tabular format in the frontend (with pagination and filters for time period, agent name, etc.)
# also add the time period thing where the admin can view 
def get_audit_trail(db = Depends(get_db)):
    cursor = db.cursor
    cursor.execute("""
    
    """)

    #== improve : to return logs for a entered time period by the user
    logs = [dict(row) for row in cursor.fetchall()]
    return {"audit_logs" : logs}