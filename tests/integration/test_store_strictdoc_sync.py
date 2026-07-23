import os
import pytest
from db import store
from integrations import strictdoc_client


@pytest.mark.integration
def test_datastore_export_to_sdoc(isolated_db, tmp_path, monkeypatch):
    """Integration test verifying DataStore records export cleanly to SDoc file format."""
    # Override get_sdoc_path to point to temporary path
    temp_sdoc = tmp_path / "requirements.sdoc"
    monkeypatch.setattr(strictdoc_client, "get_sdoc_path", lambda: str(temp_sdoc))

    req = {
        "id": "REQ-INT-001",
        "title": "Integration Test Requirement",
        "description": "Ensuring DataStore syncs with StrictDoc.",
        "type": "Requirement",
        "priority": "P1",
        "status": "in_progress"
    }
    store.create_requirement(req)

    # Export SDoc
    strictdoc_client.export_sdoc()

    assert temp_sdoc.exists()
    content = temp_sdoc.read_text(encoding="utf-8")
    assert "REQ-INT-001" in content
    assert "Integration Test Requirement" in content
