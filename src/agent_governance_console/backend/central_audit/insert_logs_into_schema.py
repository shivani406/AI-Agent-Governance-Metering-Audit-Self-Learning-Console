import hashlib
"""
Function definitions to insert logs into the three tables 
    - governance_audit_logs (hash_chaining)
    - security_incident_logs (hash_chaining)
    - usage_telemetry
    
"""

def calculate_hash(data_string :str) -> str:
    return hashlib.sha256(data_string.encode()).hexdigest()

#======== Insert logs into respective tables========

def add_governance_log(cursor, action_taken :str , approved_by :str, reason : str):
    cursor.execute("""
                    SELECT hash FROM governance_audit_logs
                   ORDER BY log_id DESC LIMIT 1
                   """)
    previous_log = cursor.fetchone()
    # keep the first hash as 0
    previous_hash = previous_log["hash"] if previous_log else "0"

    data_to_hash = f"{action_taken}{approved_by}{reason}{previous_hash}"
    current_hash = calculate_hash(data_to_hash)

    cursor.execute("""
                    INSERT INTO governance_logs (action_taken, approved_by, reason, previous_hash, hash)
                   VALUES (?,?,?,?,?)
                   """ , (action_taken, approved_by, reason, previous_hash, current_hash)
                   )
    
def add_usage_ledger(cursor, request_id: str, caller: str, target: str, status: str):
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
def add_security_incident_log(cursor, incident_type: str, description: str, involved_agents: str):

    cursor.execute("""
                INSERT INTO security_incident_logs (incident_type, description, involved_agents, previous_hash, hash)
                VALUES (?, ?, ?, ?, ?)
                """, (incident_type, description, involved_agents, previous_hash, current_hash)
                )
