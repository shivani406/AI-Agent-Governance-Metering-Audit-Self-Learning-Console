"""
Script to create data models and add sample values to our Agent database, to test initial API
"""
import hashlib
from agent_governance_console.database.db_connection import get_db_connection

def seed_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DROP TABLE IF EXISTS usage_telemetry")
    cursor.execute("DROP TABLE IF EXISTS governance_audit_logs")
    cursor.execute("DROP TABLE IF EXISTS policies")
    cursor.execute("DROP TABLE IF EXISTS agents")

    # Define Data Models
   
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT NOT NULL,
            description TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            status TEXT NOT NULL,
            reliability_score REAL NOT NULL,
            usage_count INTEGER DEFAULT 0,
            last_decision_reason TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS policies (
            policy_id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            max_cost_limit REAL NOT NULL,
            reliability_threshold REAL NOT NULL,
            FOREIGN KEY(agent_id) REFERENCES agents(agent_id)
        )
    """)

    # split the audit table into 2 parts (admin_audit_trail + Runtime_usage_audit_trail )

    # ADMINISTRATIVE AUDIT TRAIL 
    # -- Tracks explicit administrative changes (allowed, blocked, etc.)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS governance_audit_logs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        agent_id INTEGER NOT NULL,
        action_taken TEXT NOT NULL,     
        approved_by TEXT NOT NULL,     
        reason TEXT NOT NULL,           
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        previous_hash TEXT,
        hash TEXT,
        FOREIGN KEY(agent_id) REFERENCES agents(agent_id))
        """)

    # USAGE TELEMETRY AUDIT TRAIL
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_telemetry (
        telemetry_id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT NOT NULL UNIQUE, 
        caller_agent_name TEXT NOT NULL,
        target_agent_name TEXT NOT NULL,
        units_consumed INTEGER NOT NULL,
        cost REAL NOT NULL,
        status TEXT NOT NULL,            
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        previous_hash TEXT,
        hash TEXT);
        """)
    
    # to prevent tampering of audit_logs table using insert or delete commands
    log_tables = ["governance_audit_logs", "usage_telemetry"]
    for table in log_tables:
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

    # Insert Sample Data

    #== temporary for now , to test inital api

    cursor.execute("""
        INSERT OR IGNORE INTO agents (agent_id, agent_name, description, risk_level, status, reliability_score, usage_count, last_decision_reason)
        VALUES (1, 'CustomerSupportBot', 'Automated frontline user support specialist', 'high', 'active', 0.95, 0, NULL)
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO policies (policy_id, agent_id, max_cost_limit, reliability_threshold)
        VALUES (1, 1, 10.00, 0.95)
    """)

    # initial hash string for both log tables

    gov_genesis_data = "1initial_boot_allowedsystemSystem Initialization Base0"
    gov_hash = hashlib.sha256(gov_genesis_data.encode()).hexdigest()
    cursor.execute("""
        INSERT INTO governance_audit_logs (log_id, agent_id, action_taken, approved_by, reason, previous_hash, hash)
        VALUES (1, 1, 'initial_boot_allowed', 'system', 'System Initialization Base', '0', ?)
    """, (gov_hash,))
    tel_genesis_data = "0systemsystem00.0system_init_boot0"
    tel_hash = hashlib.sha256(tel_genesis_data.encode()).hexdigest()
    cursor.execute("""
        INSERT INTO usage_telemetry (telemetry_id, request_id, caller_agent_name, target_agent_name, units_consumed, cost, status, previous_hash, hash)
        VALUES (1, '0', 'system', 'system', 0, 0.0, 'system_init_boot', '0', ?)
    """, (tel_hash,))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_database()   # only need to seed the database when this script is executed as the main script
