"""
API endpoint test for M2M usage API
"""

import uuid

import pytest
from fastapi.testclient import TestClient

from agent_governance_console.backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_successful_m2m_usage_log(client):
    unique_request_id = f"test_req_{uuid.uuid4().hex[:10].upper()}"
    payload = {
        "caller": 1,
        "target": 1,
        "caller_tokens": 75,
        "target_tokens": 150,
        "request_id": unique_request_id,
    }
    response = client.post("/log-usage/", json=payload)
    assert response.status_code == 201


def test_m2m_ingestion_missing_agent_error(client):
    payload = {
        "caller": 88888,
        "target": 1,
        "caller_tokens": 100,
        "target_tokens": 100,
        "request_id": f"err_req_{uuid.uuid4().hex[:6].upper()}",
    }
    response = client.post("/log-usage/", json=payload)
    assert response.status_code == 404


# write test and add checks for invalid values (-ve tokens, non-integer caller/target, empty request_id)
@pytest.mark.parametrize(
    "invalid_field, payload_patch",
    [
        ("caller_string", {"caller": "string_instead_of_int"}),
        ("target_string", {"target": "string_instead_of_int"}),
        ("caller_tokens_negative", {"caller_tokens": -500}),
        ("target_tokens_negative", {"target_tokens": -100}),
        ("request_id_empty", {"request_id": ""}),
        ("caller_missing", {"caller": None}),
        ("request_id_missing", {"request_id": None}),
    ],
)
def test_m2m_ingestion_individual_validation_failures(
    client, invalid_field, payload_patch
):
    base_payload = {
        "caller": 1,
        "target": 1,
        "caller_tokens": 100,
        "target_tokens": 100,
        "request_id": f"valid_id_{uuid.uuid4().hex[:6].upper()}",
    }
    if payload_patch.get("caller") is None and "caller" in payload_patch:
        base_payload.pop("caller")
    elif payload_patch.get("request_id") is None and "request_id" in payload_patch:
        base_payload.pop("request_id")
    else:
        base_payload.update(payload_patch)
    response = client.post("/log-usage/", json=base_payload)
    assert response.status_code == 422


# add test for duplicate request_id to ensure idempotency
def test_m2m_idempotency_duplicate_prevention(client):
    shared_id = f"dup_id_{uuid.uuid4().hex[:6].upper()}"
    payload = {
        "caller": 1,
        "target": 1,
        "caller_tokens": 50,
        "target_tokens": 50,
        "request_id": shared_id,
    }
    first_response = client.post("/log-usage/", json=payload)
    assert first_response.status_code == 201
    second_response = client.post("/log-usage/", json=payload)
    assert second_response.status_code in [200, 400, 409]
