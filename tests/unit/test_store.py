import pytest
import sqlite3
from db import store


@pytest.mark.unit
def test_init_db_creates_tables(isolated_db):
    """Verify init_db initializes SQLite schema and tables correctly."""
    conn = sqlite3.connect(str(isolated_db))
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}
    conn.close()

    assert "requirements" in tables
    assert "test_cases" in tables
    assert "agent_runs" in tables


@pytest.mark.unit
def test_create_and_get_requirement(isolated_db, sample_requirement):
    """Test creating a requirement and retrieving it from DataStore."""
    created = store.create_requirement(sample_requirement)
    assert created["id"] == sample_requirement["id"]
    assert created["title"] == sample_requirement["title"]

    fetched = store.get_requirement(sample_requirement["id"])
    assert fetched is not None
    assert fetched["id"] == sample_requirement["id"]
    assert fetched["description"] == sample_requirement["description"]


@pytest.mark.unit
def test_update_requirement(isolated_db, sample_requirement):
    """Test updating fields on an existing requirement."""
    store.create_requirement(sample_requirement)

    updated = store.update_requirement(
        sample_requirement["id"],
        {"title": "Updated Title", "priority": "P0"}
    )
    assert updated["title"] == "Updated Title"
    assert updated["priority"] == "P0"

    fetched = store.get_requirement(sample_requirement["id"])
    assert fetched["title"] == "Updated Title"
    assert fetched["priority"] == "P0"


@pytest.mark.unit
def test_delete_requirement_cascade(isolated_db, sample_requirement):
    """Test deleting a requirement and its child items."""
    store.create_requirement(sample_requirement)
    child_req = {
        "id": "REQ-TEST-002",
        "title": "Child Requirement",
        "description": "Child description",
        "type": "Requirement",
        "parent_id": sample_requirement["id"]
    }
    store.create_requirement(child_req)

    store.delete_requirement_cascade(sample_requirement["id"])

    assert store.get_requirement(sample_requirement["id"]) is None
    assert store.get_requirement("REQ-TEST-002") is None


@pytest.mark.unit
def test_test_cases_upsert_and_retrieve(isolated_db, sample_requirement):
    """Test creating and retrieving test cases linked to a requirement."""
    store.create_requirement(sample_requirement)

    test_results = [
        {
            "id": "TC-001",
            "name": "test_feature_works",
            "status": "pass",
            "failure_message": None
        },
        {
            "id": "TC-002",
            "name": "test_feature_fails",
            "status": "fail",
            "failure_message": "Assertion Error: 1 != 2"
        }
    ]

    store.replace_test_results_for_requirement(sample_requirement["id"], test_results)

    test_cases = store.get_test_cases_for_requirement(sample_requirement["id"])
    assert len(test_cases) == 2
    names = {tc["title"] for tc in test_cases}
    assert "test_feature_works" in names
    assert "test_feature_fails" in names


@pytest.mark.unit
def test_agent_run_logging(isolated_db, sample_requirement):
    """Test creating and updating agent execution run records."""
    store.create_requirement(sample_requirement)
    run_id = store.create_agent_run(ticket_id="TICK-101", requirement_id=sample_requirement["id"])
    assert run_id is not None

    store.update_agent_run(run_id, status="success", attempts=1)

    runs = store.get_agent_runs(limit=10)
    assert len(runs) >= 1
    target = next((r for r in runs if r["ticket_id"] == "TICK-101"), None)
    assert target is not None
    assert target["status"] == "success"
