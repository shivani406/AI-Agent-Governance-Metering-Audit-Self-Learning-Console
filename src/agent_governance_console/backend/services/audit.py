"""
Handles Audit generation and SHA-256 hashing for tamper-proof logging
"""

import hashlib

def add_audit_log(cursor, agent_id, action_taken, token_count : int, approved_by):
    cursor.execute("""
                    SELECT hash FROM audit_logs
                   ORDER BY log_id DESC LIMIT 1
                   """)
    previous_log = cursor.fetchone()
    # keep the first hash as 0
    previous_hash = previous_log["hash"] if previous_log else "0"

    data_to_hash = f"{agent_id}{action_taken}{token_count}{approved_by}{previous_hash}"
    current_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()

    cursor.execute("""
                    INSERT INTO audit_logs (agent_id, action_taken, token_count, previous_hash, hash)
                   VALUES (?,?,?,?,?,?)
                   """ , (agent_id, action_taken, token_count, approved_by, previous_hash, current_hash)
                   )
    