"""
End-to-End (E2E) Integration Test Suite for User Prompt Submission & Application Stack Synthesis.
Verifies pitch deconstruction, feature resolution, AST compilation, SQLite database seeding, and domain isolation.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from onboarding.block_catalog import analyze_pitch_for_kickstart
from onboarding.dynamic_domain_generator import build_site_manifest_from_schema
from onboarding.site_ast_compiler import compile_site_manifest_to_app_tsx
from db import store


def test_chess_prompt_e2e_flow():
    """Verify complete end-to-end prompt submission pipeline for 'A chess game'."""
    pitch = "A chess game"

    # 1. Pitch Analysis & Block Recommendation
    kickstart_res = analyze_pitch_for_kickstart(pitch)
    recommended_blocks = [b['id'] for b in kickstart_res.get('blocks', []) if b.get('is_recommended') or b.get('selected')]
    assert 'catalog_grid' not in recommended_blocks, "Catalog grid MUST NOT be recommended for chess game!"

    # 2. Site Manifest Deconstruction & AST Compilation
    manifest = build_site_manifest_from_schema({'pitch': pitch})
    compiled_tsx = compile_site_manifest_to_app_tsx(manifest)

    # 3. TSX Syntax & Domain Isolation Contracts
    assert "♟️ Interactive Chess Engine" in compiled_tsx, "Interactive Chess Engine missing from compiled TSX!"
    assert "Turn: White ♔" in compiled_tsx, "Turn indicator missing from compiled TSX!"
    assert "Available Items & Offerings" not in compiled_tsx, "Catalog fallback rendered in chess game compiled TSX!"
    assert "Confirm & Place Order" not in compiled_tsx, "Cart checkout button leaked into chess game compiled TSX!"
    assert "__PRIMARY_COLOR__" not in compiled_tsx, "Unreplaced __PRIMARY_COLOR__ token in compiled TSX!"
    assert "__CATALOG_CONTAINER_JSX__" not in compiled_tsx, "Unreplaced __CATALOG_CONTAINER_JSX__ token in compiled TSX!"

    # 4. SQLite Store Seeding & Schema Constraint Verification
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
        
        # Must not raise sqlite3.IntegrityError
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


def test_pizza_prompt_e2e_flow():
    """Verify complete end-to-end prompt submission pipeline for 'A pizza ordering website'."""
    pitch = "A pizza ordering website"

    kickstart_res = analyze_pitch_for_kickstart(pitch)
    recommended_blocks = [b['id'] for b in kickstart_res.get('blocks', []) if b.get('is_recommended') or b.get('selected')]
    assert 'catalog_grid' in recommended_blocks, "Catalog grid MUST be recommended for pizza ordering!"

    manifest = build_site_manifest_from_schema({'pitch': pitch, 'enabled_features': recommended_blocks})
    compiled_tsx = compile_site_manifest_to_app_tsx(manifest)

    assert "Interactive Chess Engine" not in compiled_tsx, "Chess engine leaked into pizza ordering compiled TSX!"


def test_flappy_bird_e2e_flow():
    """Verify complete end-to-end prompt submission pipeline for 'A flappy bird game'."""
    pitch = "A flappy bird game"

    kickstart_res = analyze_pitch_for_kickstart(pitch)
    recommended_blocks = [b['id'] for b in kickstart_res.get('blocks', []) if b.get('is_recommended') or b.get('selected')]
    assert 'flappy_bird' in recommended_blocks, "Flappy bird MUST be recommended for flappy bird game!"

    manifest = build_site_manifest_from_schema({'pitch': pitch, 'enabled_features': recommended_blocks})
    compiled_tsx = compile_site_manifest_to_app_tsx(manifest)

    assert "🎮 2D Canvas Engine" in compiled_tsx, "Flappy bird canvas engine missing from compiled TSX!"
    assert "jumpFlappy" in compiled_tsx, "jumpFlappy function missing from compiled TSX!"
    assert "Available Items & Offerings" not in compiled_tsx, "Catalog tab leaked into flappy bird game compiled TSX!"
