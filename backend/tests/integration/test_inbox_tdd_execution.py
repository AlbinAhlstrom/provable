"""
Integration Test Suite for Synchronous Behavior Inbox Spec TDD Execution:
- POST /api/specs/inbox/add synchronous execution [RED -> GREEN -> Anti-Cheat -> COMMIT]
- Database state update to FULFILLED
- Five-Line Hash Lock Anti-Cheat Verification
"""

import pytest
import os
import json
from fastapi.testclient import TestClient
from main import app
from service_layer.unit_of_work import SqliteUnitOfWork
from service_layer import services
from service_layer.tdd_machine import (
    compute_test_file_hash,
    verify_test_file_integrity,
    TestTamperingError
)


def test_inbox_tdd_execution_domain_invariant_synchronous():
    """
    Submits a DOMAIN_INVARIANT specification to /api/specs/inbox/add,
    verifies that the request runs the synchronous TDD cycle,
    and asserts that the database updates cleanly to FULFILLED.
    """
    client = TestClient(app)

    payload = {
        "spec_id": "SPEC-INT-001",
        "title": "Max Pallet Weight Invariant",
        "description": "Pallet weight cannot exceed structural limits.",
        "given_when_then": "Given Pallet with id PAL-999 When validating invariants Then validate_invariants returns True",
        "target_aggregate": "Pallet",
        "spec_type": "DOMAIN_INVARIANT",
        "is_mathematical_boundary": True,
        "priority": "High"
    }

    response = client.post("/api/specs/inbox/add", json=payload)
    assert response.status_code == 201, f"Inbox add failed: {response.text}"

    data = response.json()
    assert data.get("success") is True, f"TDD execution failed: {data}"
    assert data.get("spec", {}).get("status") == "FULFILLED"


def test_hash_lock_anti_cheat_detection(tmp_path):
    """
    Verifies that modifying the test file triggers the 5-line hash lock anti-cheat error.
    """
    test_file = tmp_path / "test_sample.py"
    test_file.write_text("def test_rule(): assert 1 == 1\n", encoding="utf-8")

    initial_hash = compute_test_file_hash(str(test_file))
    assert len(initial_hash) == 64

    # Unmodified file passes verification
    assert verify_test_file_integrity(str(test_file), initial_hash) is True

    # Tamper with test file
    test_file.write_text("def test_rule(): assert True # tampered\n", encoding="utf-8")

    with pytest.raises(TestTamperingError) as exc_info:
        verify_test_file_integrity(str(test_file), initial_hash)

    assert "Anti-Cheat Violation" in str(exc_info.value)
