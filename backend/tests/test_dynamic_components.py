"""
Test suite for Step 1: Hierarchical SQLite Requirements & Dynamic Components.
"""
import pytest
import tempfile
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import store


def test_hierarchical_requirements_store():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_provable.db")
        store.set_active_db(test_db)
        store.init_db()

        # Create top-level component requirement
        req_id = store.create_component_requirement({
            "id": "REQ-FLAPPY_BIRD-001",
            "title": "Flappy Bird Game",
            "description": "Mini-game component in pizza app header",
            "canonical_key": "flappy_bird",
            "component_type": "custom",
            "meta": {"prompt": "flappy bird game"}
        })

        assert req_id == "REQ-FLAPPY_BIRD-001"

        # Verify requirement insertion in SQLite
        reqs = store.get_all_requirements()
        target = next((r for r in reqs if r["id"] == "REQ-FLAPPY_BIRD-001"), None)
        assert target is not None
        assert target["title"] == "Flappy Bird Game"
        assert target["type"] == "Folder"
        assert target["component_type"] == "custom"

        # Verify linked BDD test case
        tcs = store.get_test_cases_for_requirement("REQ-FLAPPY_BIRD-001")
        assert len(tcs) > 0
        assert tcs[0]["last_result"] == "pass"



        # Test hierarchy tree
        tree = store.get_hierarchical_requirements()
        assert any(n["id"] == "REQ-FLAPPY_BIRD-001" for n in tree)

        # Test cascading deletion
        deleted = store.delete_component_tree("flappy_bird")
        assert deleted is True
        reqs_after = store.get_all_requirements()
        assert not any(r["id"] == "REQ-FLAPPY_BIRD-001" for r in reqs_after)
