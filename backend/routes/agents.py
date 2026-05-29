from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from database.connection import get_db_connection
from backend.services.audit import write_audit_entry

router = APIRouter()

class DecisionRequest(BaseModel):
    decision: str
    reason: str
    approved_by: str

@router.get("/agents")
def get_agents():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents")
    agents = cursor.fetchall()
    result = []
    for agent in agents:
        cursor.execute("""
            SELECT COUNT(*) as total_calls,
                   COUNT(CASE WHEN status = 'success' THEN 1 END) as success_calls,
                   TOTAL(cost) as aggregate_cost,
                   TOTAL(prompt_tokens + completion_tokens) as aggregate_tokens
            FROM agent_telemetry WHERE agent_name = ?
        """, (agent["name"],))
        metrics = cursor.fetchone()
        total = metrics["total_calls"]
        reliability = 100.0 if total == 0 else (metrics["success_calls"] / total) * 100.0
        result.append({
            "name": agent["name"],
            "description": agent["description"],
            "risk_level": agent["risk_level"],
            "status": agent["status"],
            "last_decision_reason": agent["last_decision_reason"],
            "reliability_score": round(reliability, 2),
            "usage_count": total,
            "total_cost": round(metrics["aggregate_cost"], 4),
            "total_units": int(metrics["aggregate_tokens"])
        })
    conn.close()
    return result

@router.post("/agents/{name}/decision")
def update_governance(name: str, payload: DecisionRequest):
    if payload.decision not in ["allowed", "blocked", "pending_review"]:
        raise HTTPException(status_code=400, detail="Invalid governance decision")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents WHERE name = ?", (name,))
    agent = cursor.fetchone()
    if not agent:
        conn.close()
        raise HTTPException(status_code=404, detail="Agent profile missing")
    if agent["risk_level"] == "high" and not payload.reason.strip():
        conn.close()
        raise HTTPException(status_code=400, detail="Justification mandatory for high risk actions")
    cursor.execute("UPDATE agents SET status = ?, last_decision_reason = ? WHERE name = ?", (payload.decision, payload.reason, name))
    conn.commit()
    conn.close()
    write_audit_entry(f"agent_{payload.decision}", name, payload.approved_by, f"State migrated to {payload.decision}", payload.reason)
    return {"message": "Governance settings committed"}