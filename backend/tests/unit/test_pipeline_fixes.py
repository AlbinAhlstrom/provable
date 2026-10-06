"""Regression tests for pipeline defects found by tracing a real run of the babysitter prompt."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
import agent_orchestrator
from onboarding.skeleton_builder import _pluralize

# Captured at import time, before conftest's autouse fixture swaps in the hermetic mock.
_REAL_CALL_GEMINI = agent_orchestrator.call_gemini


@pytest.mark.parametrize("slug,plural", [
    ("booking", "bookings"), ("child", "children"), ("client_family", "client_families"),
    ("babysitter", "babysitters"), ("address", "addresses"), ("box", "boxes"), ("day", "days"),
    ("person", "people"), ("time_range", "time_ranges"), ("review", "reviews"),
])
def test_pluralize_generates_correct_route_names(slug, plural):
    """Verify generated resource names are real plurals, not slug + 's'.

    id: TST-FIX-001
    Given: Entity slugs from LLM-generated domains
    When: They are pluralized for routes and UoW attributes
    Then: Irregular, -y, and sibilant endings are handled
    """
    assert _pluralize(slug) == plural


def test_generated_router_uses_proper_plural_everywhere():
    """Verify routes, function names and the UoW attribute agree on the plural.

    id: TST-FIX-002
    Given: A Child aggregate
    When: Its router and the unit of work are generated
    Then: The route is /api/children and the UoW attribute is `children`, never `childs`
    """
    from onboarding.router_engine import EntitySpec
    from onboarding.skeleton_builder import generate_router_module, generate_uow_module

    ent = EntitySpec(name="Child", is_aggregate_root=True, attributes=[])
    router_src = generate_router_module(ent)
    uow_src = generate_uow_module([ent])
    assert 'prefix="/api/children"' in router_src and "def list_children" in router_src
    assert 'getattr(_uow, "children")' in router_src
    assert "self.children = repository.FakeChildRepository()" in uow_src
    assert "childs" not in router_src + uow_src


def test_kickstart_does_not_label_every_entity_an_aggregate_root(tmp_path, monkeypatch):
    """Verify the Studio only calls real aggregate roots 'Aggregate Root' and uses neutral icons.

    id: TST-FIX-003
    Given: A decomposition with one aggregate root and one non-root entity
    When: kickstart_domain_and_scaffold builds the aggregate list and it is persisted and re-read
    Then: The non-root is described as part of an aggregate, and no warehouse icons appear
    """
    from onboarding.router_engine import (
        DomainBehaviorInboxSchema, DomainStructureSchema, EntitySpec, RouterDecompositionResult,
    )
    from service_layer import services
    from service_layer.unit_of_work import FakeUnitOfWork

    structure = DomainStructureSchema(
        domain_name="Clinic",
        entities=[EntitySpec(name="Booking", is_aggregate_root=True, attributes=[]),
                  EntitySpec(name="Child", is_aggregate_root=False, attributes=[])],
        value_objects=[], enums=[])
    result = RouterDecompositionResult(structure=structure, inbox=DomainBehaviorInboxSchema(domain_name="Clinic", specs=[]))
    monkeypatch.setattr("onboarding.router_engine.decompose_pitch_into_structure_and_inbox", lambda pitch: result)

    uow = FakeUnitOfWork()
    out = services.kickstart_domain_and_scaffold(pitch="x", uow=uow, workspace_dir=str(tmp_path))
    by_name = {a["name"]: a for a in out["aggregates"]}
    assert by_name["Booking"]["is_aggregate_root"] is True and by_name["Booking"]["description"].endswith("Aggregate Root")
    assert by_name["Child"]["is_aggregate_root"] is False and "Aggregate Root" not in by_name["Child"]["description"]
    assert {a["icon"] for a in out["aggregates"]} <= {"🏛️", "🧩"}

    again = {a["name"]: a for a in services.get_active_domain_aggregates(uow=uow)["aggregates"]}
    assert again["Child"]["is_aggregate_root"] is False and again["Booking"]["is_aggregate_root"] is True


class _FakeCompletions:
    def __init__(self, fail=None):
        self.fail, self.kwargs = fail, None

    def create(self, **kwargs):
        self.kwargs = kwargs
        if self.fail:
            raise self.fail
        msg = type("M", (), {"content": "{}"})()
        return type("R", (), {"choices": [type("C", (), {"message": msg})()]})()


def _fake_openai(completions):
    class FakeOpenAI:
        def __init__(self, **_):
            self.chat = type("Chat", (), {"completions": completions})()
    return FakeOpenAI


def test_call_gemini_sends_json_mode_only_when_requested(monkeypatch):
    """Verify json_mode adds response_format and the default call does not.

    id: TST-FIX-004
    Given: A fake provider client and an API key
    When: call_gemini runs with and without json_mode
    Then: response_format={"type": "json_object"} is sent only in json mode
    """
    monkeypatch.setenv("GEMINI_API_KEY", "k" * 20)
    comp = _FakeCompletions()
    monkeypatch.setattr(agent_orchestrator, "OpenAI", _fake_openai(comp))
    _REAL_CALL_GEMINI("p", stage="s", json_mode=True)
    assert comp.kwargs["response_format"] == {"type": "json_object"}
    _REAL_CALL_GEMINI("p", stage="s")
    assert "response_format" not in comp.kwargs


def test_call_gemini_exposes_the_failure_reason(monkeypatch):
    """Verify provider errors are surfaced instead of masquerading as a missing key.

    id: TST-FIX-005
    Given: A provider that raises a quota error
    When: call_gemini fails and the router decomposition runs on the empty result
    Then: LAST_LLM_ERROR holds the real reason and the router error message includes it
    """
    from onboarding.router_engine import decompose_pitch_into_structure_and_inbox

    monkeypatch.setenv("GEMINI_API_KEY", "k" * 20)
    monkeypatch.setattr(agent_orchestrator, "OpenAI", _fake_openai(_FakeCompletions(fail=RuntimeError("429 quota exceeded"))))
    monkeypatch.setattr(agent_orchestrator, "call_gemini", _REAL_CALL_GEMINI)
    with pytest.raises(RuntimeError, match="429 quota exceeded"):
        decompose_pitch_into_structure_and_inbox("anything")
    assert "429 quota exceeded" in agent_orchestrator.LAST_LLM_ERROR
