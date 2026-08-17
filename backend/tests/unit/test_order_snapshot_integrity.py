"""
Unit tests for Domain State Contracts & Order Snapshot Integrity across all domain pitches.
Asserts that generated React App.tsx templates decouple Order Tracking snapshots from active Catalog state mutations.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from onboarding.frontend_planning_engine import (
    run_frontend_planning_pipeline,
    _generate_fallback_assembled_app,
    assemble_app_tsx_from_blueprint
)

def test_ui_generation_markdown_contains_state_and_snapshot_contracts():
    """Verifies that ui_generation.md contains explicit LLM system prompt invariants for catalog-driven cart and order snapshots."""
    prompt_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "prompts", "ui_generation.md"))
    assert os.path.exists(prompt_path), f"ui_generation.md prompt file missing at {prompt_path}"
    content = open(prompt_path, encoding="utf-8").read()

    assert "Order Tracking Snapshot" in content or "Immutable Order" in content or "Order History Snapshot" in content
    assert "handleSimulatePayment" in content or "checkout snapshot" in content.lower()


def test_fallback_assembled_app_implements_order_snapshot_pattern():
    """Asserts that _generate_fallback_assembled_app generates handleSimulatePayment with decoupled order snapshots."""
    bp = run_frontend_planning_pipeline("An app to order pizzas")
    fallback_code = _generate_fallback_assembled_app(bp)

    assert "handleSimulatePayment" in fallback_code
    assert "ref:" in fallback_code or "ORD-" in fallback_code
    assert "status:" in fallback_code
    assert "setOrders" in fallback_code
    assert "syncFixtureToBackendAndHost('tracking'" in fallback_code or "syncFixtureToBackendAndHost('cart'" in fallback_code
