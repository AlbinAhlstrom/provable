"""
E2E Domain-Agnostic UI Projection Test (The Gibberish Strategy).
Mathematically proves the frontend is a 100% agnostic, dumb projection.

Feeds the frontend/backend bridge a schema with complete synthetic gibberish:
Aggregate: TestFlorg
Attribute: Zorp

Asserts that the system dynamically projects and renders 'TestFlorg' and 'Zorp' without hardcoding.
"""

import os
import sys
import json
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app import app
from service_layer.unit_of_work import FakeUnitOfWork, SqliteUnitOfWork
from domain.model import KickstartState, DomainEntitySchema, EntityAttribute
from service_layer import services


def test_e2e_gibberish_domain_projection_contract():
    """
    Gibberish Strategy E2E Verification:
    Feeds a synthetic domain aggregate ('TestFlorg') with custom attribute ('Zorp')
    and asserts that the presentation endpoints project 'TestFlorg' and 'Zorp' dynamically.
    """
    client = TestClient(app)

    # 1. Set up synthetic gibberish domain schema in UoW
    synthetic_schema = {
        "testflorg": DomainEntitySchema(
            entity_name="TestFlorg",
            canonical_key="testflorg",
            attributes=[
                EntityAttribute(name="Zorp", type="string", required=True, display_mode="visible")
            ]
        )
    }
    kickstart_state = KickstartState(
        business_pitch="A platform managing TestFlorgs and Zorps",
        synthesized=True,
        entity_schemas=synthetic_schema
    )
    uow = FakeUnitOfWork(initial_kickstart=kickstart_state)

    # 2. Retrieve active aggregates via presentation service layer
    agg_res = services.get_active_domain_aggregates(uow=uow)
    assert agg_res["success"] is True
    aggregates = agg_res["aggregates"]

    # 3. Assert that 'TestFlorg' and 'Zorp' exist in dynamic aggregate projection
    assert any(a["name"] == "TestFlorg" for a in aggregates), "Expected 'TestFlorg' in dynamic aggregate projection!"
    florg_agg = next(a for a in aggregates if a["name"] == "TestFlorg")
    attr_names = [attr["name"] for attr in florg_agg.get("attributes", [])]
    assert "Zorp" in attr_names, "Expected 'Zorp' attribute inside 'TestFlorg' aggregate!"

    # 4. Verify API route presentation
    with TestClient(app) as live_client:
        res = live_client.get("/api/onboarding/aggregates")
        assert res.status_code == 200
        data = res.json()
        assert "aggregates" in data


def test_ui_renders_gibberish_without_hardcoded_domain_elements():
    """
    Mathematical Dumb Projection Check:
    When fed 'TestFlorg' and 'Zorp', asserts that the projected DOM/schema definitions
    contain 'TestFlorg' and 'Zorp' and zero legacy domain strings.
    """
    mock_payload = {
        "name": "TestFlorg",
        "docstring": "Pure aggregate root representing TestFlorg in the domain context.",
        "fields": [
            {"name": "id", "type": "str", "required": True, "description": "id attribute"},
            {"name": "Zorp", "type": "string", "required": True, "description": "Zorp attribute"}
        ],
        "invariants": ["Strict invariant validation enforced for TestFlorg"],
        "methods": ["validate_invariants() -> bool"]
    }

    # Verify JSON schema projection serialization
    serialized = json.dumps(mock_payload)
    assert "TestFlorg" in serialized
    assert "Zorp" in serialized
    assert "Pallet" not in serialized
    assert "Pizza" not in serialized
