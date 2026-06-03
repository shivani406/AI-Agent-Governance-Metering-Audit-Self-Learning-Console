"""
Adds sample values to our Database tables for testing and development purposes. 
This script can be run independently to reset and seed the database with initial data
It also sets up triggers to ensure that audit logs are append-only and cannot be modified or deleted
"""
import hashlib
from agent_governance_console.database.db_connection import get_db_connection

conn = get_db_connection()
cursor = conn.cursor()

def seed_database(cursor,conn):

    #== temporary for now , to test inital app
       
    cursor.execute("""
        INSERT INTO agents (agent_id, agent_name, description, risk_level, status, reliability_score, tokens_consumed, usage_count, last_decision_reason)
        VALUES (1, 'CustomerSupportBot', 'Automated frontline user support specialist', 'high', 'active', 0.95, 0, 0, NULL)
    """)
    cursor.execute("""
        INSERT INTO policies (policy_id, agent_id, max_cost_limit, reliability_threshold)
        VALUES (1, 1, 10.00, 0.95)
    """)
    conn.commit()
    conn.close()

def setup_initial_hash(conn, cursor):
    # initial hash string for both log tables

    gov_data = "1initial_boot_allowedsystemInitialization0"
    gov_hash = hashlib.sha256(gov_data.encode()).hexdigest()
    cursor.execute("""
        INSERT INTO governance_logs (log_id, agent_id, action_taken, approved_by, reason, previous_hash, hash)
        VALUES (1, 1, 'initial_boot_allowed', 'system', 'Initialization', '0', ?)
    """, (gov_hash,))
    use_data = "0systemsystem000"
    use_hash = hashlib.sha256(use_data.encode()).hexdigest()
    cursor.execute("""
        INSERT INTO usage_ledger (ledger_id, request_id, caller_agent, target_agent, caller_tokens_consumed, target_tokens_consumed, previous_hash, hash)
        VALUES (1, '0', 'system', 'system', 0, 0, '0', ?)
    """, (use_hash,))
    
    conn.commit()
    conn.close()

def setup_insert_update_security(cursor, conn):
    """
    Sets up triggers to ensure that audit logs are append-only and cannot be modified or deleted
    """
    tables = ["governance_logs", "usage_ledger", "security_incident_logs"]

    for table in tables:
        cursor.execute(f"""
            CREATE TRIGGER IF NOT EXISTS prevent_updates_{table}
            BEFORE UPDATE ON {table}
            BEGIN
                SELECT RAISE(FAIL, 'Logs are append-only and cannot be modified.');
            END;
        """)
        cursor.execute(f"""
            CREATE TRIGGER IF NOT EXISTS prevent_deletes_{table}
            BEFORE DELETE ON {table}
            BEGIN
                SELECT RAISE(FAIL, 'Logs are append-only and cannot be deleted.');
            END;
        """)
    conn.commit()
    conn.close()
if __name__ == "__main__":
    seed_database(cursor, conn)   # only need to seed the database when this script is executed as the main script
    setup_initial_hash(conn, cursor) # to set up the initial hash values for both log tables
    setup_insert_update_security(cursor, conn) # to set up triggers to prevent updates and deletes on log tables
