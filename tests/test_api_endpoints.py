"""
Pytest Files - API Endpoint test
- Using TestClient to simulate HTTP requests without opening a webserver on a port
"""

import pytest
from fastapi.testclient import TestClient

from agent_governance_console.backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_read_root_gateway_health(client):  # inject the client as dependency
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_get_all_agents(client):
    response = client.get("/agents")
    assert response.status_code == 200
    data = response.json()
    agents_list = data.get(
        "agents"
    )  # api returns a dictionary always {"agents" : agents(list(dict)) }
    assert agents_list is not None
    assert isinstance(agents_list, list)


def test_apply_governance_decision_missing_agent_error(client):
    payload = {
        "agent_id": 99999,
        "decision": "blocked",
        "reason": "Testing non-existent node targeting boundary rules",
        "approved_by": "SecurityOperator",
    }
    response = client.post("/agents/99999/decision", json=payload)
    assert response.status_code == 404


@pytest.mark.parametrize(
    "invalid_case, payload_patch",
    [
        ("invalid_decision_string", {"decision": "not_a_valid_status"}),
        ("decision_missing", {"decision": None}),
        ("reason_missing", {"reason": None}),
        ("approved_by_missing", {"approved_by": None}),
    ],
)
def test_apply_governance_decision_individual_validation_failures(
    client, invalid_case, payload_patch
):
    base_payload = {
        "agent_id": 1,
        "decision": "blocked",
        "reason": "Administrative enforcement validation checks",
        "approved_by": "ClusterAdmin",
    }
    if "decision" in payload_patch and payload_patch["decision"] is None:
        base_payload.pop("decision")
    elif "reason" in payload_patch and payload_patch["reason"] is None:
        base_payload.pop("reason")
    elif "approved_by" in payload_patch and payload_patch["approved_by"] is None:
        base_payload.pop("approved_by")
    else:
        base_payload.update(payload_patch)
    response = client.post("/agents/1/decision", json=base_payload)
    assert response.status_code == 422


def test_usage_metering(client):
    response = client.get("/usage")
    assert response.status_code == 200


def test_fetch_complete_audit_trail(client):
    response = client.get("/audit-log")
    assert response.status_code == 200
    data = response.json()
    assert "usage-ledger" in data
    assert "governance_logs" in data
    assert "security_incident_logs" in data
