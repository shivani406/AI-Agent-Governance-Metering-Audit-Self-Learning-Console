import hashlib
"""
Function definitions to insert logs into the three tables 
    - governance_audit_logs (hash_chaining)
    - security_incident_logs (hash_chaining)
    - usage_ledger 
"""

def calculate_hash(data_string :str) -> str:
    return hashlib.sha256(data_string.encode()).hexdigest()

#======== Insert logs into respective tables========

def add_governance_log(cursor, agent_id, action_taken :str , approved_by :str, reason : str):
    cursor.execute("""
                    SELECT hash FROM governance_logs
                   ORDER BY log_id DESC LIMIT 1
                   """)
    previous_log = cursor.fetchone()
    # keep the first hash as 0
    previous_hash = previous_log["hash"] if previous_log else "0"

    data_to_hash = f"{agent_id}{action_taken}{approved_by}{reason}{previous_hash}"
    current_hash = calculate_hash(data_to_hash)

    cursor.execute("""
                    INSERT INTO governance_logs (agent_id, action_taken, approved_by, reason, previous_hash, hash)
                   VALUES (?,?,?,?,?,?)
                   """ , (agent_id, action_taken, approved_by, reason, previous_hash, current_hash)
                   )
    
    
def add_usage_ledger(cursor, request_id: str, caller_agent: int, target_agent: int, caller_tokens_consumed: int, target_tokens_consumed: int):
    cursor.execute("""
                   SELECT hash FROM usage_ledger ORDER BY ledger_id DESC LIMIT 1
                   """)
    previous_log = cursor.fetchone()
    previous_hash = previous_log["hash"] if previous_log else "0"
    data_to_hash = f"{request_id}{caller_agent}{target_agent}{caller_tokens_consumed}{target_tokens_consumed}{previous_hash}"
    current_hash = calculate_hash(data_to_hash)
    cursor.execute("""
                INSERT INTO usage_ledger (request_id, caller_agent, target_agent, caller_tokens_consumed, target_tokens_consumed, previous_hash, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (request_id, caller_agent, target_agent, caller_tokens_consumed, target_tokens_consumed, previous_hash, current_hash)
                )
    

def add_security_incident_log(cursor, incident_type: str, description: str, caller_agent: int = None, target_agent: int = None):

    cursor.execute("""
                INSERT INTO security_incident_logs (incident_type, caller_agent, target_agent, description)
                VALUES (?, ?, ?, ?)
                """, (incident_type, caller_agent, target_agent, description)
                )
