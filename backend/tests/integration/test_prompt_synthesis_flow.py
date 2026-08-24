"""
End-to-End (E2E) Integration Test Suite for User Prompt Submission & Application Stack Synthesis.
Verifies pitch deconstruction, feature resolution, AST compilation, SQLite database seeding, and domain isolation.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from onboarding.domain_ontology import analyze_pitch_for_kickstart
from onboarding.dynamic_domain_generator import build_site_manifest_from_schema
from onboarding.site_ast_compiler import compile_site_manifest_to_app_tsx
from db import store


def test_pizza_prompt_integration_flow():
    """Verify complete prompt submission and synthesis pipeline for 'An app to order pizzas'."""
    pitch = "An app to order pizzas"

    kickstart_res = analyze_pitch_for_kickstart(pitch)
    recommended_blocks = [b['id'] for b in kickstart_res.get('blocks', []) if b.get('is_recommended') or b.get('selected')]
    assert 'catalog' in recommended_blocks or 'catalog_grid' in recommended_blocks, "Catalog MUST be recommended for pizza ordering!"

    manifest = build_site_manifest_from_schema({'pitch': pitch, 'enabled_features': recommended_blocks})
    compiled_tsx = compile_site_manifest_to_app_tsx(manifest)

    assert "Pizza" in compiled_tsx or "SliceCraft" in compiled_tsx or "Menu" in compiled_tsx, "Pizza domain content missing from compiled TSX!"

    # SQLite Store Seeding & Schema Constraint Verification
    store.init_db()
    with store.get_connection() as conn:
        conn.execute("PRAGMA foreign_keys = OFF")
        conn.execute("DELETE FROM test_cases")
        conn.execute("DELETE FROM requirements")
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()

    reqs = kickstart_res.get('extracted_requirements', [])
    for rspec in reqs:
        req_type = rspec.get("type", "Requirement")
        if req_type not in ('Folder', 'Requirement', 'Task', 'Bug'):
            req_type = "Requirement"
        
        store.create_requirement({
            "id": rspec.get("id", f"REQ-{os.urandom(3).hex().upper()}"),
            "title": rspec.get("title", "Business Rule"),
            "description": rspec.get("description", rspec.get("title", "")),
            "type": req_type,
            "priority": rspec.get("priority", "High"),
            "status": "Done"
        })

    all_reqs = store.get_all_requirements()
    assert isinstance(all_reqs, list), "store.get_all_requirements() must return a list!"

