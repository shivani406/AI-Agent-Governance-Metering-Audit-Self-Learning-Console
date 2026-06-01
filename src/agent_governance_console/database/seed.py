"""
Script to create data models and add sample values to our Agent database, to test initial API
"""
import hashlib
from agent_governance_console.database.connection import get_db_connection

def seed_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Define Data Models
    # == Data models to be improved further
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

    # RUNTIME USAGE AUDIT TRAIL
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_telemetry (
        telemetry_id INTEGER PRIMARY KEY AUTOINCREMENT,
        request_id TEXT NOT NULL UNIQUE, -- Prevents duplicate counting cleanly!
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
    cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS prevent_log_updates
                    BEFORE UPDATE ON usage_telemetry
                    BEGIN
                        SELECT RAISE(FAIL, 'Audit logs are append-only and cannot be modified.');
                    END;
                    """)
    
    cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS prevent_log_deletes
                    BEFORE DELETE ON usage_telemetry
                    BEGIN
                        SELECT RAISE(FAIL, 'Audit logs are append-only and cannot be deleted.');
                    END;
                    """)
    cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS prevent_log_updates
                    BEFORE UPDATE ON governance_audit_logs
                    BEGIN
                        SELECT RAISE(FAIL, 'Audit logs are append-only and cannot be modified.');
                    END;
                    """)
    
    cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS prevent_log_deletes
                    BEFORE DELETE ON governance_audit_logs
                    BEGIN
                        SELECT RAISE(FAIL, 'Audit logs are append-only and cannot be deleted.');
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
    # initial hash string

    data_to_hash = "11Initial System Boot0system0"

    initial_hash = hashlib.sha256(data_to_hash.encode()).hexdigest()
    cursor.execute("""
        INSERT OR IGNORE INTO audit_logs (log_id, policy_id, agent_id, token_count, approved_by, action_taken, previous_hash, hash)
        VALUES (1, 1, 1, 0, 'system', 'Initial System Boot', '0', ?)
    """, (initial_hash,))
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_database()   # only need to seed the database when this script is executed as the main script
