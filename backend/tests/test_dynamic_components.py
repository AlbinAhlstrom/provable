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


def test_step2_api_component_flow():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_provable2.db")
        store.set_active_db(test_db)
        store.init_db()

        from main import add_dynamic_component, ComponentAddRequest, delete_dynamic_component, ComponentDeleteRequest, get_component_suggestions
        add_res = add_dynamic_component(ComponentAddRequest(prompt="Flappy bird game", component_type="custom"))
        assert add_res["success"] is True
        assert add_res["canonical_key"] == "flappy_bird_game"
        assert add_res["component_type"] == "custom"

        reqs = store.get_all_requirements()
        assert any(r["id"] == "REQ-CMP-FLAPPY_BIRD_GAME-001" for r in reqs)

        sug_res = get_component_suggestions()
        assert sug_res["success"] is True
        assert len(sug_res["suggestions"]) >= 3

        del_res = delete_dynamic_component(ComponentDeleteRequest(canonical_key="flappy_bird_game"))
        assert del_res["success"] is True

        reqs_after = store.get_all_requirements()
        assert not any(r["id"] == "REQ-CMP-FLAPPY_BIRD_GAME-001" for r in reqs_after)


def test_step3_sidebar_api_contracts():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_provable3.db")
        store.set_active_db(test_db)
        store.init_db()

        store.create_component_requirement({
            "id": "REQ-CMP-PAYMENT_SYSTEM-001",
            "title": "Payment System",
            "description": "Stripe/PayPal payment gateway component",
            "canonical_key": "payment_system",
            "component_type": "custom",
            "meta": {"prompt": "Payment system"}
        })

        reqs = store.get_all_requirements()
        active_ids = [r["id"] for r in reqs if r["status"] != "Disabled"]
        assert "REQ-CMP-PAYMENT_SYSTEM-001" in active_ids

        from main import delete_dynamic_component, ComponentDeleteRequest
        res = delete_dynamic_component(ComponentDeleteRequest(canonical_key="payment_system"))
        assert res["success"] is True

        reqs_after = store.get_all_requirements()
        assert not any(r["id"] == "REQ-CMP-PAYMENT_SYSTEM-001" for r in reqs_after)


def test_step4_modular_component_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        test_db = os.path.join(tmpdir, "test_provable4.db")
        store.set_active_db(test_db)
        store.init_db()

        from main import get_active_domain_params, get_workspace_base
        from onboarding.dynamic_domain_generator import generate_universal_domain_files
        
        ws = get_workspace_base()
        schema = get_active_domain_params()
        files = generate_universal_domain_files(schema, ws)
        
        assert any("App.tsx" in k for k in files.keys())
        
        app_path = os.path.join(ws, 'src', 'App.tsx')
        assert app_path in files
        assert "enabledFeatures" in files[app_path]



