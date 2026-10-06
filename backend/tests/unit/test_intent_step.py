"""The intent step decides what kind of product a pitch asks for BEFORE the domain model is designed."""

import json
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
import agent_orchestrator
from onboarding import intent as intent_mod
from onboarding.intent import IntentError, ProductIntent, classify_pitch_intent, intent_block
from onboarding.router_engine import (
    DomainBehaviorInboxSchema, DomainStructureSchema, EntitySpec, RouterDecompositionResult,
    decompose_pitch_into_structure_and_inbox,
)
from service_layer import services
from service_layer.unit_of_work import FakeUnitOfWork

GOOD = {
    "product_type": "public_website",
    "audience": "families looking for childcare",
    "primary_goal": "Let visitors learn about the firm and send an inquiry.",
    "scope_summary": "A public site presenting services and caregivers with an inquiry form.",
    "model_focus": ["services offered", "caregiver profiles", "visitor inquiries"],
    "out_of_scope": ["internal staff scheduling"],
    "assumptions": ["No online payments"],
}


def _llm(monkeypatch, payload):
    seen = {}

    def fake(prompt, stage="general", **options):
        seen.update(prompt=prompt, stage=stage, options=options)
        return payload if isinstance(payload, str) else json.dumps(payload)

    monkeypatch.setattr(agent_orchestrator, "call_gemini", fake)
    return seen


# ── classifier ───────────────────────────────────────────────────────────────────────────────────
def test_classifier_returns_a_structured_intent(monkeypatch):
    """Verify the pitch is classified through the intent prompt in JSON mode.

    id: TST-INT-001
    Given: An LLM that answers with a valid intent
    When: classify_pitch_intent runs
    Then: A ProductIntent is returned and the call used the intent stage with JSON mode
    """
    seen = _llm(monkeypatch, GOOD)
    result = classify_pitch_intent("A personal website for a babysitters firm")
    assert isinstance(result, ProductIntent) and result.product_type == "public_website"
    assert result.model_focus[0] == "services offered" and result.out_of_scope == ["internal staff scheduling"]
    assert seen["stage"] == "intent_classification" and seen["options"].get("json_mode") is True
    assert "A personal website for a babysitters firm" in seen["prompt"]


@pytest.mark.parametrize("payload,needle", [
    ({**GOOD, "product_type": "spaceship"}, "product_type"),
    ({k: v for k, v in GOOD.items() if k != "scope_summary"}, "scope_summary"),
    ({**GOOD, "model_focus": []}, "model_focus"),
    ("not json at all", "valid JSON"),
    ("", "intent classification failed"),
])
def test_classifier_fails_loudly_on_unusable_answers(monkeypatch, payload, needle):
    """Verify there is no guessed default intent.

    id: TST-INT-002
    Given: An unknown type, a missing field, an empty focus list, non-JSON, or an empty answer
    When: classify_pitch_intent runs
    Then: IntentError names the problem (never a silent fallback type)
    """
    _llm(monkeypatch, payload)
    monkeypatch.setattr(agent_orchestrator, "LAST_LLM_ERROR", None, raising=False)
    with pytest.raises(IntentError, match=f"(?i){needle}"):
        classify_pitch_intent("anything")


def test_intent_block_lists_scope_and_exclusions():
    """Verify the text injected into the decomposition prompt carries the scope decisions.

    id: TST-INT-003
    Given: A ProductIntent
    When: It is rendered for the router prompt
    Then: Type, audience, model focus and the do-not-model list appear
    """
    text = intent_block(ProductIntent.from_dict(GOOD))
    for needle in ("public_website", "families looking for childcare", "caregiver profiles", "internal staff scheduling", "Do NOT model"):
        assert needle in text
    assert "not specified" in intent_block(None).lower()


# ── prompts ──────────────────────────────────────────────────────────────────────────────────────
def _prompt(name):
    return open(os.path.join(os.path.dirname(intent_mod.__file__), "..", "prompts", name), encoding="utf-8").read()


def test_intent_prompt_enumerates_the_allowed_types():
    """Verify the classifier prompt and the validator agree on the allowed product types.

    id: TST-INT-004
    Given: The intent prompt and the validator's allowed types
    When: Compared
    Then: Every allowed type appears in the prompt
    """
    text = _prompt("intent_classification.md")
    assert all(t in text for t in intent_mod.PRODUCT_TYPES) and "{business_pitch}" in text


def test_router_prompt_scopes_the_model_by_intent(monkeypatch):
    """Verify decomposition receives the intent and is told to respect exclusions.

    id: TST-INT-005
    Given: A ProductIntent
    When: decompose_pitch_into_structure_and_inbox builds its prompt
    Then: The intent block is in the prompt, and without an intent the prompt says it is not specified
    """
    decomposition = {"structure": {"domain_name": "D", "entities": [], "value_objects": []}, "inbox": {"domain_name": "D", "specs": []}}
    seen = _llm(monkeypatch, decomposition)
    decompose_pitch_into_structure_and_inbox("pitch", intent=ProductIntent.from_dict(GOOD))
    assert "internal staff scheduling" in seen["prompt"] and "caregiver profiles" in seen["prompt"]
    decompose_pitch_into_structure_and_inbox("pitch")
    assert "not specified" in seen["prompt"].lower()


# ── persistence and API ──────────────────────────────────────────────────────────────────────────
def test_kickstart_classifies_first_and_stores_the_intent(monkeypatch, tmp_path):
    """Verify kickstart runs the intent step, feeds the decomposition, and persists/returns the intent.

    id: TST-INT-006
    Given: A stubbed classifier and decomposition
    When: kickstart_domain_and_scaffold runs and the aggregates are read back
    Then: The decomposition received the intent, the result and the stored state carry it
    """
    order, received = [], {}
    monkeypatch.setattr("onboarding.intent.classify_pitch_intent", lambda pitch: order.append("intent") or ProductIntent.from_dict(GOOD))

    def fake_decompose(pitch, intent=None):
        order.append("decompose")
        received["intent"] = intent
        return RouterDecompositionResult(
            structure=DomainStructureSchema(domain_name="D", entities=[EntitySpec(name="Service", is_aggregate_root=True, attributes=[])], value_objects=[], enums=[]),
            inbox=DomainBehaviorInboxSchema(domain_name="D", specs=[]))

    monkeypatch.setattr("onboarding.router_engine.decompose_pitch_into_structure_and_inbox", fake_decompose)
    uow = FakeUnitOfWork()
    out = services.kickstart_domain_and_scaffold(pitch="x", uow=uow, workspace_dir=str(tmp_path))
    assert order == ["intent", "decompose"] and received["intent"].product_type == "public_website"
    assert out["intent"]["product_type"] == "public_website"
    assert services.get_active_domain_aggregates(uow=uow)["intent"]["scope_summary"] == GOOD["scope_summary"]


def test_intent_survives_the_database_round_trip():
    """Verify the intent column persists through the SQLite repository.

    id: TST-INT-007
    Given: A KickstartState with an intent saved through the SQLite repository
    When: It is read back
    Then: The intent is identical
    """
    from adapters.repository import SqliteKickstartRepository
    from domain.model import KickstartState
    repo = SqliteKickstartRepository()
    repo.save(KickstartState(business_pitch="p", intent=GOOD, synthesized=True))
    assert repo.get().intent == GOOD
