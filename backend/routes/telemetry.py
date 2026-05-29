from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from database.connection import get_db_connection
from backend.services.audit import write_audit_entry
router = APIRouter()

class TelemetryRequest(BaseModel):
    caller: str
    target: str
    prompt_tokens: int
    completion_tokens: int
    execution_status: str
    execution_time_ms: int
    request_id: str

@router.post("/usage")
def process_telemetry(payload: TelemetryRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_telemetry WHERE request_id = ?", (payload.request_id,))
    
    if cursor.fetchone():
        conn.close()
        write_audit_entry("duplicate_usage_ignored", payload.target, payload.caller, "Deduplication triggered", "Dropped transaction duplicate")
        return {"message": "Telemetry structural packet duplicate"}
    cursor.execute("SELECT * FROM agents WHERE name = ?", (payload.target,))
    agent = cursor.fetchone()
    if not agent:
        conn.close()
        write_audit_entry("usage_rejected", payload.target, payload.caller, "Denied execution", "Target missing")
        raise HTTPException(status_code=404, detail="Target agent unregistered")
    if agent["status"] == "blocked":
        cursor.execute("""
            INSERT INTO agent_telemetry (request_id, agent_name, caller, status, prompt_tokens, completion_tokens, cost, execution_time_ms, timestamp)
            VALUES (?, ?, ?, ?, 0, 0, 0.0, 0, ?)
        """, (payload.request_id, payload.target, payload.caller, "failed_blocked", datetime.utcnow().isoformat()))
        conn.commit()
        conn.close()
        write_audit_entry("usage_rejected", payload.target, payload.caller, "Blocked context run", "Active governance block")
        raise HTTPException(status_code=403, detail="Target system administratively blocked")
    calculated_cost = (payload.prompt_tokens * agent["input_token_rate"]) + (payload.completion_tokens * agent["output_token_rate"])
    
    cursor.execute("""
        INSERT INTO agent_telemetry (request_id, agent_name, caller, status, prompt_tokens, completion_tokens, cost, execution_time_ms, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (payload.request_id, payload.target, payload.caller, payload.execution_status, payload.prompt_tokens, payload.completion_tokens, calculated_cost, payload.execution_time_ms, datetime.utcnow().isoformat()))
    
    cursor.execute("""
        SELECT COUNT(*) as total, COUNT(CASE WHEN status = 'success' THEN 1 END) as success
        FROM (SELECT status FROM agent_telemetry WHERE agent_name = ? ORDER BY timestamp DESC LIMIT 10)
    """, (payload.target,))
    window = cursor.fetchone()

    if window["total"] >= 5:
        rolling_rate = (window["success"] / window["total"]) * 100.0
        if rolling_rate < 60.0 and agent["status"] == "allowed":
            cursor.execute("UPDATE agents SET status = 'pending_review', last_decision_reason = 'Automated breaker tripped' WHERE name = ?", (payload.target,))
            write_audit_entry("agent_pending_review", payload.target, "system_learning_core", "Breaker active", f"Rolling metric fell to {rolling_rate:.1f}%")
    conn.commit()
    conn.close()
    write_audit_entry("usage_logged", payload.target, payload.caller, "Telemetry updated", f"Cost metric: ${calculated_cost:.6f}")
    return {"message": "Metrics tracked successfully"}

@router.get("/usage-summary")
def get_summary():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT agent_name, COUNT(*) as count, TOTAL(prompt_tokens + completion_tokens) as tokens, TOTAL(cost) as cost
        FROM agent_telemetry WHERE status != 'failed_blocked' GROUP BY agent_name
    """)

    rows = cursor.fetchall()
    summary = {row["agent_name"]: {"usage_count": row["count"], "total_units": int(row["tokens"]), "total_cost": round(row["cost"], 4)} for row in rows}
    conn.close()
    return summary