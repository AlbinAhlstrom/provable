"""One review of the whole spec set reports contradictions up front; it never rewrites specs or retries."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import agent_orchestrator
from onboarding.router_engine import BusinessSpec
from onboarding.spec_review import review_spec_consistency


def _spec(i, gwt):
    return BusinessSpec(spec_id=f"S{i}", title=f"T{i}", description="d", given_when_then=gwt, target_aggregate="Enquiry")


SPECS = [_spec(1, "Given no email When submitted Then it is accepted"), _spec(2, "Given no email When submitted Then it is rejected")]


def _llm(monkeypatch, reply):
    calls = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda p, stage="general", **k: calls.append((stage, p)) or reply)
    return calls


def test_contradictions_are_reported_with_their_spec_ids(monkeypatch):
    """Verify a contradicting pair is reported and the model sees every spec.

    id: TST-REV-010
    Given: Two specs with opposite outcomes and a model that names them
    When: The set is reviewed
    Then: The conflict lists both ids and the reason; the prompt contained both specs
    """
    calls = _llm(monkeypatch, '{"conflicts": [{"specs": ["S1", "S2", "S-unknown"], "reason": "accepted vs rejected"}]}')
    result = review_spec_consistency(SPECS)
    assert result == {"success": True, "conflicts": [{"specs": ["S1", "S2"], "reason": "accepted vs rejected"}]}
    assert len(calls) == 1 and "S1" in calls[0][1] and "S2" in calls[0][1]


def test_single_spec_needs_no_review_and_failures_are_not_retried(monkeypatch):
    """Verify trivial sets skip the call and provider/parse failures are reported after one call.

    id: TST-REV-011
    Given: One spec; then an empty answer; then invalid JSON
    When: Each is reviewed
    Then: No call for one spec; one call each for the failures, each reported as success False
    """
    calls = _llm(monkeypatch, "")
    assert review_spec_consistency(SPECS[:1]) == {"success": True, "conflicts": []} and not calls
    assert review_spec_consistency(SPECS)["success"] is False and len(calls) == 1
    calls = _llm(monkeypatch, "not json")
    assert review_spec_consistency(SPECS)["success"] is False and len(calls) == 1


def test_verification_models_say_whether_test_and_code_are_independent(monkeypatch):
    """Verify the summary states honestly whether one model wrote both the test and the code.

    id: TST-REV-012
    Given: The same model, then different models, for the test and code stages
    When: The verification models are read
    Then: independent is False, then True
    """
    from service_layer import services
    for var in ("LLM_MODEL_RED_TEST_GENERATION", "LLM_MODEL_GREEN_CODE_REPAIR"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("LLM_MODEL", "m1")
    assert services.verification_models() == {"test": "m1", "code": "m1", "independent": False}
    monkeypatch.setenv("LLM_MODEL_RED_TEST_GENERATION", "m2")
    assert services.verification_models() == {"test": "m2", "code": "m1", "independent": True}
