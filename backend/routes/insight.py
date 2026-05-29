from fastapi import APIRouter
import math
from database.connection import get_db_connection

router = APIRouter()

@router.get("/improvement-suggestions")
def process_insights():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agents")
    agents = cursor.fetchall()
    suggestions = []
    for agent in agents:
        name = agent["name"]
        cursor.execute("SELECT cost, status FROM agent_telemetry WHERE agent_name = ?", (name,))
        history = cursor.fetchall()
        total = len(history)
        success = len([r for r in history if r["status"] == "success"])
        blocked = len([r for r in history if r["status"] == "failed_blocked"])
        reliability = 100.0 if total == 0 else (success / total) * 100.0
        if reliability < 70.0 and total > 0:
            suggestions.append({
                "agent_name": name,
                "type": "reliability_risk",
                "severity": "critical",
                "suggestion": f"Live accuracy tracking low ({reliability:.1f}%). Execution context recommendations suggest model rollback."
            })
        if blocked > 3:
            suggestions.append({
                "agent_name": name,
                "type": "policy_drift",
                "severity": "high",
                "suggestion": f"Detected {blocked} context call attempts on blocked targets. Route map configuration update required."
            })
        if total >= 3:
            costs = [r["cost"] for r in history if r["status"] == "success"]
            if costs:
                avg = sum(costs) / len(costs)
                variance = sum((c - avg) ** 2 for c in costs) / len(costs)
                std_dev = math.sqrt(variance)
                cursor.execute("SELECT cost FROM agent_telemetry WHERE agent_name = ? ORDER BY timestamp DESC LIMIT 1", (name,))
                latest = cursor.fetchone()
                if latest and latest["cost"] > (avg + (2 * std_dev)) and std_dev > 0:
                    suggestions.append({
                        "agent_name": name,
                        "type": "cost_bloat",
                        "severity": "medium",
                        "suggestion": f"Latest request signature cost ${latest['cost']:.4f}, breaking baseline boundaries. Inspect model prompt structure loops."
                    })
        if agent["status"] == "pending_review":
            suggestions.append({
                "agent_name": name,
                "type": "deadlock",
                "severity": "low",
                "suggestion": "Agent remains stalled in validation workflows. Administrative ownership allocation suggested."
            })
    conn.close()
    return suggestions