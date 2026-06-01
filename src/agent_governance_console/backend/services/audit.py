"""
Handles Audit generation and SHA-256 hashing for tamper-proof logging
"""

import hashlib

def calculate_hash(data_string :str) -> str:
    return hashlib.sha256(data_string.encode()).hexdigest()
# to add logs 
def add_governance_log(cursor, agent_id : int, action_taken :str , approved_by :str, reason : str):
    cursor.execute("""
                    SELECT hash FROM governance_audit_logs
                   ORDER BY log_id DESC LIMIT 1
                   """)
    previous_log = cursor.fetchone()
    # keep the first hash as 0
    previous_hash = previous_log["hash"] if previous_log else "0"

    data_to_hash = f"{agent_id}{action_taken}{approved_by}{reason}{previous_hash}"
    current_hash = calculate_hash(data_to_hash)

    cursor.execute("""
                    INSERT INTO governanceaudit_logs (agent_id, action_taken, approved_by, reason, previous_hash, hash)
                   VALUES (?,?,?,?,?,?,?)
                   """ , (agent_id, action_taken, approved_by, reason, previous_hash, current_hash)
                   )
    
def add_telemetry_log(cursor, request_id: str, caller: str, target: str, units: int, cost: float, status: str):
    cursor.execute("""
                   SELECT hash FROM usage_telemetry ORDER BY telemetry_id DESC LIMIT 1
                   """)
    previous_log = cursor.fetchone()
    previous_hash = previous_log["hash"] if previous_log else "0"
    data_to_hash = f"{request_id}{caller}{target}{units}{cost}{status}{previous_hash}"
    current_hash = calculate_hash(data_to_hash)
    cursor.execute("""
                INSERT INTO usage_telemetry (request_id, caller_agent_name, target_agent_name, units_consumed, cost, status, previous_hash, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (request_id, caller, target, units, cost, status, previous_hash, current_hash)
                )