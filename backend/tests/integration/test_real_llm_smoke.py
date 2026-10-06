"""Opt-in smoke test that exercises the real LLM path (no mocks).

Everything else in the suite mocks the LLM (see conftest.py), so nothing else proves
that the prompts still produce output the parsers accept. This test costs a few cents,
so it only runs when explicitly requested:

    RUN_LLM_SMOKE=1 GEMINI_API_KEY=... python -m pytest backend/tests/integration/test_real_llm_smoke.py

It also needs an API key (LLM_API_KEY / OPENAI_API_KEY / GEMINI_API_KEY); optionally
OPENAI_BASE_URL and LLM_MODEL select the provider.
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
import agent_orchestrator

# Captured at import (collection) time, before conftest's autouse fixture swaps in the mock.
_REAL_CALL_GEMINI = agent_orchestrator.call_gemini

_HAS_KEY = any(os.environ.get(k) for k in ("LLM_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY"))

pytestmark = [
    pytest.mark.llm,
    pytest.mark.skipif(os.environ.get("RUN_LLM_SMOKE") != "1",
                       reason="opt-in: set RUN_LLM_SMOKE=1 to spend real LLM tokens"),
    pytest.mark.skipif(not _HAS_KEY, reason="no LLM API key in environment"),
]

PITCH = "A small clinic booking system. A Patient can book an Appointment with a Doctor. A Doctor cannot be double-booked at the same time."


@pytest.fixture(autouse=True)
def real_llm(monkeypatch):
    """Undo the hermetic mock for this module so calls reach the real provider."""
    monkeypatch.setattr(agent_orchestrator, "call_gemini", _REAL_CALL_GEMINI)
    # Modules that did `from agent_orchestrator import call_gemini` hold their own reference.
    for modname in ("onboarding.domain_ontology", "onboarding.frontend_planning_engine",
                    "onboarding.requirement_generator", "onboarding.code_verifier"):
        mod = sys.modules.get(modname)
        if mod is not None and hasattr(mod, "call_gemini"):
            monkeypatch.setattr(mod, "call_gemini", _REAL_CALL_GEMINI)


def test_router_decomposition_with_real_llm():
    """Verify the router prompt yields a parseable, domain-specific decomposition.

    id: TST-LLM-001
    Given: A short business pitch and a real LLM provider
    When: The pitch is decomposed into structure and behavior inbox
    Then: Entities and BDD specs come back, using the pitch's own vocabulary
    """
    from onboarding.router_engine import decompose_pitch_into_structure_and_inbox

    result = decompose_pitch_into_structure_and_inbox(PITCH)
    names = {e.name.lower() for e in result.structure.entities}
    assert names, "no entities returned"
    assert names & {"patient", "appointment", "doctor"}, f"entities ignore the pitch vocabulary: {names}"
    assert result.inbox.specs, "no behavior specs returned"
    for spec in result.inbox.specs:
        text = spec.given_when_then.lower()
        assert "given" in text and "when" in text and "then" in text


def test_domain_ontology_with_real_llm():
    """Verify the ontology prompt yields a spec the parser accepts.

    id: TST-LLM-002
    Given: The same pitch and a real LLM provider
    When: The domain ontology is stormed
    Then: A master entity with attributes and at least one capability is produced
    """
    from onboarding.domain_ontology import storm_domain_ontology

    ont = storm_domain_ontology(PITCH)
    assert ont.master_entity.entity_name
    assert ont.master_entity.attributes
    assert ont.capabilities
