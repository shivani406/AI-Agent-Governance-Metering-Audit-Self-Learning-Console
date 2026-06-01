"""
Script to create data models and add sample values to our Agent database, to test initial API
"""
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            policy_id INTEGER,
            agent_id INTEGER NOT NULL,
            token_count INTEGER NOT NULL,
            approved_by TEXT, NOT NULL
            action_taken TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            previous_hash TEXT,
            hash TEXT,
            FOREIGN KEY(policy_id) REFERENCES policies(policy_id),
            FOREIGN KEY(agent_id) REFERENCES agents(agent_id)
        )
    """)

    # to prevent tampering of audit_logs table using insert or delete commands
    cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS prevent_log_updates
                    BEFORE UPDATE ON audit_logs
                    BEGIN
                        SELECT RAISE(FAIL, 'Audit logs are append-only and cannot be modified.');
                    END;
                    """)
    
    cursor.execute("""
                    CREATE TRIGGER IF NOT EXISTS prevent_log_deletes
                    BEFORE DELETE ON audit_logs
                    BEGIN
                        SELECT RAISE(FAIL, 'Audit logs are append-only and cannot be deleted.');
                    END;
                    """)

    # Insert Sample Data

    #== temporary for now , to test inital api

    cursor.execute("""
        INSERT OR IGNORE INTO agents (agent_id, agent_name, status, total_cost_spent)
        VALUES (1, 'CustomerSupportBot', 'active', 0.125)
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO policies (policy_id, agent_id, max_cost_limit, reliability_threshold)
        VALUES (1, 1, 10.00, 0.95)
    """)
    cursor.execute("""
        INSERT OR IGNORE INTO audit_logs (log_id, policy_id, agent_id, token_count, action_taken)
        VALUES (1, 1, 1, 350, 'Request Authorized')
    """)
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    seed_database()   # only need to seed the database when this script is executed as the main script
