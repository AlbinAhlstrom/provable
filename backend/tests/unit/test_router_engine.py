import pytest
from onboarding.router_engine import (
    decompose_pitch_into_structure_and_inbox,
    DomainStructureSchema,
    DomainBehaviorInboxSchema,
    BusinessSpec,
    EntitySpec
)

def test_router_engine_decomposes_pizza_pitch():
    pitch = "A pizzeria application where customers order pizzas with custom toppings, size pricing multipliers, and minimum order amount of $15."
    result = decompose_pitch_into_structure_and_inbox(pitch)
    
    assert isinstance(result.structure, DomainStructureSchema)
    assert isinstance(result.inbox, DomainBehaviorInboxSchema)
    
    # Assert structural separation (entities)
    entity_names = [e.name for e in result.structure.entities]
    assert any("Pizza" in name or "Order" in name for name in entity_names)
    
    # Assert behavior inbox extraction
    assert len(result.inbox.specs) >= 2
    spec_titles = [s.title.lower() for s in result.inbox.specs]
    assert any("multiplier" in t or "size" in t or "minimum" in t or "topping" in t for t in spec_titles)
    
    # Check spec contract
    first_spec = result.inbox.specs[0]
    assert isinstance(first_spec, BusinessSpec)
    assert first_spec.spec_id.startswith("SPEC-")
    assert first_spec.target_aggregate != ""
    assert "Given" in first_spec.given_when_then or "given" in first_spec.given_when_then.lower()

def test_router_engine_flags_mathematical_boundary_rules():
    pitch = "FIFO inventory system where batch shelf-life expires after 30 days and hazardous class 3 materials cannot exceed 500kg per zone."
    result = decompose_pitch_into_structure_and_inbox(pitch)
    
    assert isinstance(result.structure, DomainStructureSchema)
    assert isinstance(result.inbox, DomainBehaviorInboxSchema)
    
    # Assert mathematical / range boundary flag is recognized
    math_specs = [s for s in result.inbox.specs if s.is_mathematical_boundary]
    assert len(math_specs) >= 1


def test_router_engine_decomposes_wms_baseline_pitch():
    """
    Standard Benchmark — Industrial WMS Domain Baseline:
    Decomposes into pure domain entities (Pallet, Zone, Operator) without pre-guessed complex rules.
    """
    pitch = "An industrial warehouse management system to track Pallets, storage Zones, and forklift Operators."
    result = decompose_pitch_into_structure_and_inbox(pitch)

    assert isinstance(result.structure, DomainStructureSchema)
    assert isinstance(result.inbox, DomainBehaviorInboxSchema)

    entity_names = [e.name for e in result.structure.entities]
    assert "Pallet" in entity_names
    assert "Zone" in entity_names
    assert "Operator" in entity_names

    # Check specs and typed mutation fields
    assert len(result.inbox.specs) >= 2
    for s in result.inbox.specs:
        assert isinstance(s, BusinessSpec)
        assert s.spec_type in ["ATTRIBUTE_EXPANSION", "DOMAIN_INVARIANT", "STATE_TRANSITION", "API_CONTRACT"]


def test_router_engine_raises_on_llm_synthesis_failure(monkeypatch):
    """
    Fail Loudly Invariant:
    Refuses to silently fallback to generic 'Item' when LLM call fails or returns empty.
    """
    import agent_orchestrator
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda *args, **kwargs: "")

    with pytest.raises(RuntimeError, match="LLM synthesis failed. Refusing to fallback to generic 'Item'."):
        decompose_pitch_into_structure_and_inbox("Some arbitrary pitch")

