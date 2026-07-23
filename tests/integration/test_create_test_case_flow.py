import os
import pytest
from db import store


@pytest.mark.integration
def test_create_test_case_integration_flow(api_client, isolated_db, tmp_path, monkeypatch):
    """REQ-TST-002: Integration test for create-test-case API flow linking requirement to failing TDD test spec."""
    req_id = "REQ-TST-002"
    req_payload = {
        "id": req_id,
        "title": "Automated TDD Test Spec Generation Flow",
        "description": "Backend generates failing BDD test cases linked to requirements.",
        "type": "Requirement",
        "priority": "High",
        "status": "Backlog"
    }
    store.create_requirement(req_payload)

    # Mock call_gemini to return a valid pytest BDD string
    mock_test_code = """
def test_created_bdd_flow():
    \"\"\"
    Given: Feature configured properly
    When: Action executed
    Then: Expected result verified
    \"\"\"
    assert False, "Failing TDD initial spec"
"""
    import agent_orchestrator
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, **kwargs: mock_test_code)

    # Call create-test-case API endpoint
    response = api_client.post(f"/api/requirements/{req_id}/create-test-case", json={
        "given": "Feature configured properly",
        "when": "Action executed",
        "then": "Expected result verified"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "test_case_id" in data
    assert "test_code" in data

    # Verify test case was persisted in SQLite DataStore
    test_cases = store.get_test_cases_for_requirement(req_id)
    assert len(test_cases) >= 1
    tc = test_cases[0]
    assert tc["requirement_id"] == req_id
    assert tc["last_result"] == "fail"
