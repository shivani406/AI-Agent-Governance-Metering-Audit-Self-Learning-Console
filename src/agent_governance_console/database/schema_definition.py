"""
Define all the Data Models
- Agents: Stores details about each agent, including its name, description, risk level, status (allowed/blocked), reliability score, usage count, and last decision reason.
- Policies: Stores policy parameters for each agent, such as maximum cost limits and reliability thresholds.
- governance_logs (The Admin Ledger)
- usage_ledger (The Accounting Ledger)
- security_incident_logs (The Alert & Triage Sheet)

"""

from agent_governance_console.database.db_connection import get_db_connection

def create_schema():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Define Data Models
   
    # cursor.execute("DROP TABLE IF EXISTS policies")
    # cursor.execute("DROP TABLE IF EXISTS agents")
    # cursor.execute("DROP TABLE IF EXISTS governance_logs")
    # cursor.execute("DROP TABLE IF EXISTS usage_ledger")
    # cursor.execute("DROP TABLE IF EXISTS security_incident_logs")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
                   agent_id INTEGER PRIMARY KEY AUTOINCREMENT,
                   agent_name TEXT NOT NULL UNIQUE,
                   description TEXT NOT NULL,
                   risk_level TEXT NOT NULL,
                   status TEXT NOT NULL,
                   reliability_score REAL NOT NULL,
                   tokens_consumed INTEGER DEFAULT 0,
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

    #=======AUDIT TABLES========

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS governance_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            action_taken TEXT NOT NULL,
            approved_by TEXT NOT NULL,
            reason TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            previous_hash TEXT,
            hash TEXT,
            FOREIGN KEY(agent_id) REFERENCES agents(agent_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usage_ledger (
            ledger_id INTEGER PRIMARY KEY AUTOINCREMENT, -- database token
            request_id TEXT NOT NULL UNIQUE,   --network token (to detect duplicates)
            caller_agent int NOT NULL,
            target_agent int NOT NULL,
            caller_tokens_consumed INTEGER NOT NULL,
            target_tokens_consumed INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            previous_hash TEXT,
            hash TEXT,
            FOREIGN KEY(caller_agent) REFERENCES agents(agent_id),
            FOREIGN KEY(target_agent) REFERENCES agents(agent_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS security_incident_logs (
            incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_type TEXT NOT NULL,  --blocked_agent_call, missing_agent, etc
            caller_agent int,   
            target_agent int,
            description TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(caller_agent) REFERENCES agents(agent_id),
            FOREIGN KEY(target_agent) REFERENCES agents(agent_id)            
        )
    """)