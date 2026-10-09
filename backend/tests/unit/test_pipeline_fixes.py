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
    monkeypatch.setattr("onboarding.router_engine.decompose_pitch_into_structure_and_inbox", lambda pitch, intent=None: result)

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


def test_reasoning_effort_defaults_to_low_and_is_configurable(monkeypatch):
    """Verify hidden-reasoning cost is capped by default and can be overridden or disabled.

    id: TST-FIX-006
    Given: A fake provider client
    When: call_gemini runs by default, with LLM_REASONING_EFFORT=high, and with it set empty
    Then: reasoning_effort is "low", "high", and omitted respectively
    """
    monkeypatch.setenv("GEMINI_API_KEY", "k" * 20)
    comp = _FakeCompletions()
    monkeypatch.setattr(agent_orchestrator, "OpenAI", _fake_openai(comp))
    monkeypatch.delenv("LLM_REASONING_EFFORT", raising=False)
    _REAL_CALL_GEMINI("p", stage="s")
    assert comp.kwargs["reasoning_effort"] == "low"
    monkeypatch.setenv("LLM_REASONING_EFFORT", "high")
    _REAL_CALL_GEMINI("p", stage="s")
    assert comp.kwargs["reasoning_effort"] == "high"
    monkeypatch.setenv("LLM_REASONING_EFFORT", "")
    _REAL_CALL_GEMINI("p", stage="s")
    assert "reasoning_effort" not in comp.kwargs


def test_a_call_is_given_the_time_its_reasoning_effort_needs(monkeypatch):
    """Verify raising the effort does not make calls that finished at low effort time out.

    id: TST-FIX-031
    Given: A fake provider client
    When: call_gemini runs at the default effort, with LLM_REASONING_EFFORT=medium, and with an explicit timeout
    Then: The request waits 60 s, longer than 60 s, and exactly the explicit time respectively
    """
    monkeypatch.setenv("GEMINI_API_KEY", "k" * 20)
    comp = _FakeCompletions()
    monkeypatch.setattr(agent_orchestrator, "OpenAI", _fake_openai(comp))
    monkeypatch.delenv("LLM_REASONING_EFFORT", raising=False)
    _REAL_CALL_GEMINI("p", stage="s")
    assert comp.kwargs["timeout"] == 60.0
    monkeypatch.setenv("LLM_REASONING_EFFORT", "medium")
    _REAL_CALL_GEMINI("p", stage="s")
    assert comp.kwargs["timeout"] == 180.0
    _REAL_CALL_GEMINI("p", stage="s", timeout_s=45.0)
    assert comp.kwargs["timeout"] == 45.0
    monkeypatch.delenv("LLM_REASONING_EFFORT")
    _REAL_CALL_GEMINI("p", stage="s", reasoning_effort="high")
    assert comp.kwargs["timeout"] > 180.0


def test_provider_that_rejects_reasoning_effort_fails_loudly_without_retry(monkeypatch):
    """Verify an unsupported parameter is reported once, with the fix, and never silently retried.

    id: TST-FIX-007
    Given: A provider that errors when reasoning_effort is sent
    When: call_gemini runs
    Then: Exactly one request is made, "" is returned, and LAST_LLM_ERROR names LLM_REASONING_EFFORT
    """
    monkeypatch.setenv("GEMINI_API_KEY", "k" * 20)
    monkeypatch.delenv("LLM_REASONING_EFFORT", raising=False)
    calls = []

    class Picky:
        def create(self, **kwargs):
            calls.append(dict(kwargs))
            raise RuntimeError("Unrecognized request argument supplied: reasoning_effort")

    monkeypatch.setattr(agent_orchestrator, "OpenAI", _fake_openai(Picky()))
    assert _REAL_CALL_GEMINI("p", stage="s") == ""
    assert len(calls) == 1
    assert "LLM_REASONING_EFFORT" in agent_orchestrator.LAST_LLM_ERROR


def test_sdk_automatic_retries_are_disabled(monkeypatch):
    """Verify the provider client is built with max_retries=0 so failures are never masked.

    id: TST-FIX-008
    Given: A recording stand-in for the OpenAI client
    When: call_gemini constructs the client
    Then: max_retries is 0
    """
    monkeypatch.setenv("GEMINI_API_KEY", "k" * 20)
    seen = {}

    class Recorder(_fake_openai(_FakeCompletions())):
        def __init__(self, **kwargs):
            seen.update(kwargs)
            super().__init__(**kwargs)

    monkeypatch.setattr(agent_orchestrator, "OpenAI", Recorder)
    _REAL_CALL_GEMINI("p", stage="s")
    assert seen.get("max_retries") == 0


def test_the_failure_reason_belongs_to_the_thread_that_made_the_call():
    """Verify stages running in parallel cannot clear or overwrite each other's failure reason.

    id: TST-FIX-020
    Given: One thread whose LLM call failed
    When: Another thread records a success before the first reads its reason
    Then: The first thread still reads its own reason
    """
    import threading
    seen = {}

    def failing():
        agent_orchestrator.LAST_LLM_ERROR = "429 quota exceeded"
        other = threading.Thread(target=lambda: setattr(agent_orchestrator, "LAST_LLM_ERROR", None))
        other.start()
        other.join()
        seen["reason"] = agent_orchestrator.LAST_LLM_ERROR

    worker = threading.Thread(target=failing)
    worker.start()
    worker.join()
    assert seen["reason"] == "429 quota exceeded"


def test_hidden_reasoning_tokens_are_recorded(monkeypatch, tmp_path):
    """Verify thinking the provider bills but does not return is visible (a 7-token answer that took 4 s).

    id: TST-FIX-021
    Given: A provider whose usage totals 120 tokens for a 10-token prompt and a 30-token answer
    When: call_gemini is traced
    Then: The call's meta holds total_tokens 120 and reasoning_tokens 80
    """
    import glob
    import json
    import types
    monkeypatch.setenv("GEMINI_API_KEY", "k" * 20)
    monkeypatch.setenv("PROVABLE_TRACE_DIR", str(tmp_path))
    usage = types.SimpleNamespace(prompt_tokens=10, completion_tokens=30, total_tokens=120)
    response = types.SimpleNamespace(usage=usage, choices=[types.SimpleNamespace(
        finish_reason="stop", message=types.SimpleNamespace(content="ok"))])

    class Completions:
        def create(self, **kwargs):
            return response

    monkeypatch.setattr(agent_orchestrator, "OpenAI", _fake_openai(Completions()))
    assert _REAL_CALL_GEMINI("p", stage="s") == "ok"
    meta = json.load(open(glob.glob(str(tmp_path / "*.json"))[0]))["meta"]
    assert meta["total_tokens"] == 120 and meta["reasoning_tokens"] == 80


def test_reading_the_aggregates_never_calls_the_llm(monkeypatch):
    """Verify a read the Studio polls costs nothing (four stray decompositions of the default pitch ran during a kickstart).

    id: TST-FIX-022
    Given: A kickstart state with nothing synthesized
    When: The aggregates are read
    Then: The answer is an empty list and the decomposition is not called
    """
    from onboarding import router_engine
    from service_layer import services
    from service_layer.unit_of_work import FakeUnitOfWork
    calls = []
    monkeypatch.setattr(router_engine, "decompose_pitch_into_structure_and_inbox", lambda *a, **k: calls.append(a))
    result = services.get_active_domain_aggregates(uow=FakeUnitOfWork())
    assert result["success"] is True and result["aggregates"] == [] and calls == []


def test_call_gemini_sends_a_schema_when_the_stage_has_one(monkeypatch):
    """Verify a stage with a typed answer asks the provider to hold the answer to that schema.

    id: TST-FIX-JSON-SCHEMA
    Given: A fake provider client and an API key
    When: call_gemini runs with a json_schema
    Then: response_format is the json_schema form carrying that schema (json_object alone let an answer with trailing
          commas through, which sank a whole build)
    """
    monkeypatch.setenv("GEMINI_API_KEY", "k" * 20)
    comp = _FakeCompletions()
    monkeypatch.setattr(agent_orchestrator, "OpenAI", _fake_openai(comp))
    schema = {"type": "object", "properties": {"a": {"type": "string"}}, "required": ["a"]}
    _REAL_CALL_GEMINI("p", stage="domain_engine_synthesis", json_schema=schema)
    sent = comp.kwargs["response_format"]
    assert sent["type"] == "json_schema" and sent["json_schema"]["schema"] == schema and sent["json_schema"]["name"]
