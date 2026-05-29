"""
Initialize the sample seed values of AI-agent telemeters
"""

import sqlite3
from connection import DB_PATH

def initialize_and_seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            name TEXT PRIMARY KEY,
            description TEXT,
            risk_level TEXT,
            status TEXT,
            last_decision_reason TEXT,
            input_token_rate REAL,
            output_token_rate REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_telemetry (
            request_id TEXT PRIMARY KEY,
            agent_name TEXT,
            caller TEXT,
            status TEXT,
            prompt_tokens INTEGER,
            completion_tokens INTEGER,
            cost REAL,
            execution_time_ms INTEGER,
            timestamp TEXT,
            FOREIGN KEY(agent_name) REFERENCES agents(name)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            event_type TEXT,
            agent_name TEXT,
            actor TEXT,
            action TEXT,
            reason TEXT
        )
    """)

    seed_agents = seed_agents = [
        ("DocParser", "Parses incoming PDF invoices", "low", "allowed", "Initial setup", 5.00/1000000, 15.00/1000000),
        ("CodeReviewer", "Automated PR code analysis", "medium", "pending_review", "System evaluation needed", 2.50/1000000, 10.00/1000000),
        ("DataAnonymizer", "Removes PII from logs", "high", "blocked", "Security compliance hold", 10.00/1000000, 30.00/1000000),
        ("TrendAnalyzer", "Market trend prediction engine", "medium", "allowed", "Production baseline", 15.00/1000000, 60.00/1000000)
    ]
    cursor.executemany("""
        INSERT OR IGNORE INTO agents 
        (name, description, risk_level, status, last_decision_reason, input_token_rate, output_token_rate)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, seed_agents)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    initialize_and_seed()