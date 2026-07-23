import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Set test environment variables before imports
os.environ["OPENAI_API_KEY"] = "sk-test-mock-key-1234567890"
os.environ["PYTHONIOENCODING"] = "utf-8"

from db import store
from main import app
import agent_orchestrator
import onboarding.workspace_discovery_agent as workspace_discovery_agent


@pytest.fixture(autouse=True)
def isolated_db(tmp_path, monkeypatch):
    """Fixture to ensure every test runs against a clean, isolated temporary SQLite database."""
    db_file = tmp_path / "test_provable.db"
    dummy_json = tmp_path / "non_existent_requirements.json"
    
    # Mock LLM calls so tests don't require external API credentials
    mock_llm_response = "[]"
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt: mock_llm_response)
    monkeypatch.setattr(workspace_discovery_agent, "call_gemini", lambda prompt: mock_llm_response)
    
    monkeypatch.setattr(store, "REQUIREMENTS_JSON", str(dummy_json))
    store.set_active_db(str(db_file))
    store.init_db()
    
    yield db_file
    
    # Cleanup global state
    store._active_db_path = None


@pytest.fixture
def api_client(isolated_db):
    """FastAPI TestClient fixture using isolated database."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
def sample_requirement():
    """Returns sample requirement data payload."""
    return {
        "id": "REQ-TEST-001",
        "title": "Test Requirement Title",
        "description": "Test requirement description for autotesting.",
        "type": "Requirement",
        "priority": "P1",
        "status": "Backlog",
        "parent_id": None
    }
