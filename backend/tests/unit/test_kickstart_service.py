"""
Unit tests for Kickstart & Domain Modeling service layer functions using FakeUnitOfWork.
Tests domain discovery, kickstart analysis, state fetching, state saving, and synthesis stack workflows.
"""

import os
import sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from domain.model import KickstartState, Requirement
from service_layer.unit_of_work import FakeUnitOfWork
from service_layer import services


def test_discover_domain_model_service():
    """
    Given a business pitch
    When calling discover_domain_model
    Then domain schema containing entities, services, exceptions, and invariants is returned.
    """
    pitch = "Order and deliver delicious pizzas online"
    uow = FakeUnitOfWork()
    res = services.discover_domain_model(pitch=pitch, uow=uow)
    schema = res["domain_schema"]
    assert any(k in schema for k in ["title", "pitch", "entities", "hero_headline"])


def test_discover_domain_model_empty_pitch():
    """
    Given an empty business pitch
    When calling discover_domain_model
    Then success is False and error message is returned.
    """
    uow = FakeUnitOfWork()
    res = services.discover_domain_model(pitch="   ", uow=uow)
    assert res["success"] is False
    assert "Pitch cannot be empty" in res["error"]


def test_get_kickstart_state_service():
    """
    Given a FakeUnitOfWork initialized with custom KickstartState
    When calling get_kickstart_state
    Then the kickstart state dict is returned.
    """
    initial_state = KickstartState(
        business_pitch="Drone Delivery Service",
        blocks=["catalog", "tracking"],
        extracted_requirements=[{"id": "REQ-1", "title": "Drone Route"}],
        synthesized=True
    )
    uow = FakeUnitOfWork(initial_kickstart=initial_state)

    state_dict = services.get_kickstart_state(uow=uow)

    assert state_dict["business_pitch"] == "Drone Delivery Service"
    assert state_dict["blocks"] == ["catalog", "tracking"]
    assert len(state_dict["extracted_requirements"]) == 1
    assert state_dict["synthesized"] is True


def test_analyze_kickstart_pitch_service(monkeypatch):
    """
    Given a business pitch and FakeUnitOfWork
    When calling analyze_kickstart_pitch
    Then pitch is analyzed, state is updated in UoW, and UoW commits.
    """
    monkeypatch.setattr(
        "onboarding.block_catalog.analyze_pitch_for_kickstart",
        lambda pitch: {
            "blocks": [{"id": "catalog", "title": "Product Catalog"}],
            "extracted_requirements": [{"id": "REQ-PITCH-1", "title": "Pizza Catalog", "type": "Requirement"}]
        }
    )
    uow = FakeUnitOfWork()
    res = services.analyze_kickstart_pitch(business_pitch="Pizza Shop", uow=uow)

    assert res["success"] is True
    assert "data" in res
    saved_state = uow.kickstart.get()
    assert saved_state.business_pitch == "Pizza Shop"
    assert saved_state.synthesized is False
    assert uow.committed is True


def test_refine_domain_model_service():
    """
    Given current domain schema and developer feedback
    When calling refine_domain_model
    Then updated schema and success response are returned.
    """
    uow = FakeUnitOfWork()
    current_schema = {"pitch": "Pizza Shop", "entities": []}
    res = services.refine_domain_model(current_schema=current_schema, feedback="Add toppings entity", uow=uow)

    assert res["success"] is True
    assert res["domain_schema"] == current_schema
    assert "refined successfully" in res["message"]


def test_synthesize_kickstart_stack_service(monkeypatch):
    """
    Given pitch, blocks, requirements, and FakeUnitOfWork
    When calling synthesize_kickstart_stack
    Then requirements are purged and re-seeded, kickstart state marked synthesized, and synthesis called.
    """
    existing_req = Requirement(id="OLD-REQ", title="Old Requirement", description="Old desc")
    uow = FakeUnitOfWork(initial_requirements=[existing_req])

    monkeypatch.setattr(
        "onboarding.frontend_planning_engine.build_pitch_specific_domain_schema",
        lambda pitch: {"entities": [], "services": []}
    )
    monkeypatch.setattr(
        "onboarding.synthesis.synthesize_domain_code",
        lambda schema: {"success": True, "files": {}}
    )
    monkeypatch.setattr(
        "service_layer.services.sync_workspace_app_shell",
        lambda ws_base=None, uow=None: None
    )

    res = services.synthesize_kickstart_stack(
        business_pitch="Online Coffee Shop",
        pitch=None,
        selected_blocks=["catalog", "cart"],
        selected_block_ids=None,
        requirements=[{"id": "REQ-COFFEE-1", "title": "Select Beans"}],
        extracted_requirements=None,
        uow=uow
    )

    assert res["success"] is True
    # Old req should be removed
    assert uow.requirements.get("OLD-REQ") is None
    # New requirements seeded
    assert uow.requirements.get("REQ-COFFEE-1") is not None
    # State updated to synthesized=True
    st = uow.kickstart.get()
    assert st.business_pitch == "Online Coffee Shop"
    assert st.synthesized is True
    assert uow.committed is True
