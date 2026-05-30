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
            status TEXT NOT NULL,
            total_cost_spent REAL DEFAULT 0.0
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
            action_taken TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(policy_id) REFERENCES policies(policy_id),
            FOREIGN KEY(agent_id) REFERENCES agents(agent_id)
        )
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
