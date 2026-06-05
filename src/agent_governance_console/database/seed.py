"""
Adds sample values to our Database tables for testing and development purposes.
This script can be run independently to reset and seed the database with initial data
It also sets up triggers to ensure that audit logs are append-only and cannot be modified or deleted
"""

import hashlib

from agent_governance_console.database.db_connection import get_db_connection
from agent_governance_console.database.schema_definition import create_schema


def seed_database(cursor):

    # == temporary for now , to test inital app

    cursor.execute("""
        INSERT INTO agents (agent_id, agent_name, description, risk_level, status, reliability_score, tokens_consumed, usage_count, last_decision_reason)
        VALUES (1, 'CustomerSupportBot', 'Automated frontline user support specialist', 'high', 'active', 0.95, 124500, 412, NULL)
    """)
    cursor.execute("""
        INSERT INTO agents (agent_id, agent_name, description, risk_level, status, reliability_score, tokens_consumed, usage_count, last_decision_reason)
        VALUES (2, 'PaymentProcessorAgent', 'Handles transactional tokenizations and secure invoice verification checking', 'high', 'active', 0.99, 85000, 198, NULL)
    """)
    cursor.execute("""
        INSERT INTO agents (agent_id, agent_name, description, risk_level, status, reliability_score, tokens_consumed, usage_count, last_decision_reason)
        VALUES (3, 'DataScraperBot', 'Experimental pipeline worker aggregating regional supply chain intelligence insights', 'low', 'pending_review', 0.72, 412000, 89, 'High latency and unoptimized recursion patterns flagged by gateway telemetry')
    """)
    cursor.execute("""
        INSERT INTO agents (agent_id, agent_name, description, risk_level, status, reliability_score, tokens_consumed, usage_count, last_decision_reason)
        VALUES (4, 'MarketingCopyGen', 'Generates bulk outreach drafts and customer engagement email variants', 'low', 'active', 0.88, 12050, 45, NULL)
    """)
    cursor.execute("""
        INSERT INTO agents (agent_id, agent_name, description, risk_level, status, reliability_score, tokens_consumed, usage_count, last_decision_reason)
        VALUES (5, 'MaliciousTestAgent', 'Simulated rogue agent configured to hammer API vectors with anomalous contextual nesting', 'high', 'blocked', 0.31, 984000, 1542, 'Exceeded concurrent token extraction policy parameters three times sequentially')
    """)

    cursor.execute("""
        INSERT INTO policies (policy_id, agent_id, max_cost_limit, reliability_threshold)
        VALUES (1, 1, 10.00, 0.95)
    """)
    cursor.execute("""
        INSERT INTO policies (policy_id, agent_id, max_cost_limit, reliability_threshold)
        VALUES (2, 2, 50.00, 0.98)
    """)
    cursor.execute("""
        INSERT INTO policies (policy_id, agent_id, max_cost_limit, reliability_threshold)
        VALUES (3, 3, 5.00, 0.85)
    """)
    cursor.execute("""
        INSERT INTO policies (policy_id, agent_id, max_cost_limit, reliability_threshold)
        VALUES (4, 4, 100.00, 0.80)
    """)
    cursor.execute("""
        INSERT INTO policies (policy_id, agent_id, max_cost_limit, reliability_threshold)
        VALUES (5, 5, 0.00, 0.99)
    """)


def setup_initial_hash(cursor):
    # initial hash string for both log tables

    gov_data = "1initial_boot_allowedsystemInitialization0"
    gov_hash = hashlib.sha256(gov_data.encode()).hexdigest()
    cursor.execute(
        """
        INSERT INTO governance_logs (log_id, agent_id, action_taken, approved_by, reason, previous_hash, hash)
        VALUES (1, 1, 'initial_boot_allowed', 'system', 'Initialization', '0', ?)
    """,
        (gov_hash,),
    )
    use_data = "011000"
    use_hash = hashlib.sha256(use_data.encode()).hexdigest()
    cursor.execute(
        """
        INSERT INTO usage_ledger (ledger_id, request_id, caller_agent, target_agent, caller_tokens_consumed, target_tokens_consumed, previous_hash, hash)
        VALUES (1, '0', 1, 1, 0, 0, '0', ?)
    """,
        (use_hash,),
    )


def setup_insert_update_security(cursor):
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


if __name__ == "__main__":
    create_schema()
    conn = get_db_connection()
    cursor = conn.cursor()

    # cursor.execute("DELETE FROM security_incident_logs")
    # cursor.execute("DELETE FROM usage_ledger")
    # cursor.execute("DELETE FROM governance_logs")
    # cursor.execute("DELETE FROM policies")
    # cursor.execute("DELETE FROM agents")
    seed_database(
        cursor
    )  # only need to seed the database when this script is executed as the main script
    setup_initial_hash(cursor)  # to set up the initial hash values for both log tables
    setup_insert_update_security(
        cursor
    )  # to set up triggers to prevent updates and deletes on log tables
    conn.commit()
    conn.close()
