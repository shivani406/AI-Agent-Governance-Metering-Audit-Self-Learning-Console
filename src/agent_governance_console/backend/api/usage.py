"""
Provides an endpoint to retrieve usage summaries for all agents
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


@router.get("/usage-summary", status_code=200)
def get_usage_summary(db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("""
                    SELECT agent_name, usage_count, tokens_consumed FROM agents
                   """)

    summary = [dict(row) for row in cursor.fetchall()]
    return {"summary": summary}


# to be further improved using client side filters for time period, agent name, etc.
# and also to fetch data from usage_ledger for more detailed summary
