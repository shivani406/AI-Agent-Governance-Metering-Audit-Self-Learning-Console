# AI Agent Governance, Metering & Audit Console

A secure, high-performance enterprise governance gateway and telemetry tracking engine designed to regulate internal Agent-to-Agent (Service-to-Service) execution workflows. This platform features structural circuit breakers, real-time metrics capture, anti-inflation idempotency validation, and dual-ledger cryptographic hash chaining to maintain a tamper-evident audit trail.

## 🏗️ System Architecture

The console separates operational concerns into two isolated, high-speed transactional persistence layers to prevent data model coupling:

1. **Administrative Governance Chain (`governance_audit_logs`)**: Captures human-in-the-loop authorization changes (`agent_allowed`, `agent_blocked`), enforcement levels, and mandatory policy justifications.
2. **Runtime Operations Chain (`usage_telemetry`)**: Tracks micro-agent telemetry data (`units_consumed`, `cost`, downstream targets) and validation drops natively at the circuit-breaker perimeter.

Both ledgers enforce cryptographic data integrity by linking rows sequentially via continuous SHA-256 blocks (`previous_hash` ➡️ `hash`) combined with append-only database engines.

---

## ⚡ Key Features & Core Rules

### 🛠️ Agent Governance Engine
* **High-Risk Guardrails**: System components flagged with `risk_level: "high"` cannot be authorized to `allowed` status without an explicit, non-empty justification string. Any empty strings trigger an immediate `400 Bad Request` drop.
* **Granular Lifecycle Mapping**: Regulates active machine processing states across strict operational lifecycles (`active`, `blocked`, `pending_review`).

### 📊 Real-Time Metering Gateway
* **Automated Circuit Breaking**: Machine-to-machine requests originating from an agent currently marked as `blocked` are stopped instantly at the gateway perimeter with an `403 Forbidden` response.
* **Anti-Inflation Idempotency**: Evaluates a unique `request_id` identifier across incoming telemetry payloads. If a duplicate identifier is captured, the engine logs the attempt as `duplicate_usage_ignored` but skips updating metrics to ensure budget figures remain accurate.
* **Dynamic Metric Tracking**: Updates runtime execution counts (`usage_count`) across agent metadata cleanly upon authorized handshakes.

---

## 📦 Project Directory Layout

```text
AI-Agent-Governance-Metering-Audit-Self-Learning-Console/
├── src/
│   └── agent_governance_console/
│       ├── __init__.py
│       ├── backend/
│       │   ├── __init__.py
│       │   ├── main.py                  # FastAPI Application Gateway
│       │   ├── routes/
│       │   │   ├── __init__.py
│       │   │   ├── agents.py            # Governance Policy Endpoints
│       │   │   ├── usage.py             # Telemetry & Metering Processor
│       │   │   └── audit.py             # Unified Audit View Router
│       │   └── services/
│       │       ├── __init__.py
│       │       └── audit.py             # SHA-256 Cryptographic Hash Service
│       └── database/
│           ├── __init__.py
│           ├── connection.py            # SQLite Connection Configuration
│           └── seed.py                  # Schema Blueprint & Genesis Block Seeder
├── pyproject.toml                       # Poetry Package Configuration
└── README.md                            # Documentation Deployment Guide