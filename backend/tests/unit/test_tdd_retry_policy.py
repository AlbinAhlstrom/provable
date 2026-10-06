"""Retry policy of the TDD loop: at most one retry, only on a GREEN-gate rejection, fed with that verdict."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from onboarding.router_engine import BusinessSpec
from service_layer import tdd_machine

CLASS_CODE = "@dataclass\nclass Widget:\n    id: str = ''\n"


def _spec():
    return BusinessSpec(
        spec_id="SPEC-RP-1", title="t", description="d", given_when_then="Given a When b Then c",
        target_aggregate="Widget", spec_type="DOMAIN_INVARIANT", is_mathematical_boundary=False, priority="High",
    )


@pytest.fixture
def scripted(monkeypatch):
    """Script the gate verdicts and record every call to the LLM-backed synthesizer."""
    calls = {"synth": []}

    def install(green_verdicts, synth_error=None):
        verdicts = iter(green_verdicts)

        def fake_synth(extracted_class, target_class_name, spec, failure_output):
            calls["synth"].append(failure_output)
            if synth_error:
                raise synth_error
            return CLASS_CODE

        monkeypatch.setattr(tdd_machine, "synthesize_green_class_implementation", fake_synth)
        monkeypatch.setattr(tdd_machine, "run_isolated_pytest",
                            lambda path, cwd=None: {"exit_code": 1, "stderr": "pytest-output", "report": None})
        monkeypatch.setattr(tdd_machine, "evaluate_red_gate_result",
                            lambda *a, **k: {"approved": True, "status": "APPROVED_RED", "reason": "red"})
        monkeypatch.setattr(tdd_machine, "evaluate_green_gate_result",
                            lambda *a, **k: {"approved": next(verdicts), "status": "G", "reason": "assert failed"})
        return calls

    return install


def test_first_attempt_success_makes_a_single_llm_call(scripted, tmp_path):
    """Verify a passing first attempt never triggers a retry.

    id: TST-RP-001
    Given: A GREEN gate that approves immediately
    When: The loop runs
    Then: The synthesizer is called once and the spec is FULFILLED
    """
    calls = scripted([True])
    result = tdd_machine.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert result["status"] == "FULFILLED" and len(calls["synth"]) == 1 and len(result["attempts"]) == 1


def test_one_feedback_retry_is_allowed_and_receives_the_gate_verdict(scripted, tmp_path):
    """Verify exactly one retry happens, and it is told why the first attempt was rejected.

    id: TST-RP-002
    Given: A GREEN gate that rejects once and then approves
    When: The loop runs
    Then: The synthesizer is called twice and the second call's feedback carries the rejection
    """
    calls = scripted([False, True])
    result = tdd_machine.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert result["status"] == "FULFILLED"
    assert len(calls["synth"]) == 2 and len(result["attempts"]) == 2
    assert "previous GREEN attempt was rejected" in calls["synth"][1] and "assert failed" in calls["synth"][1]


def test_never_a_third_attempt(scripted, tmp_path):
    """Verify a second rejection ends the loop in a visible dead end instead of retrying again.

    id: TST-RP-003
    Given: A GREEN gate that always rejects
    When: The loop runs
    Then: The synthesizer is called exactly twice and the spec requires human intervention
    """
    calls = scripted([False, False, False, False])
    result = tdd_machine.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert len(calls["synth"]) == 2
    assert result["success"] is False and result["status"] == "REQUIRES_HUMAN_INTERVENTION" and result["phase"] == "DEAD_END"
    assert [a["approved"] for a in result["attempts"]] == [False, False] and len(result["error_log"]) == 2


def test_provider_errors_are_not_retried(scripted, tmp_path):
    """Verify an error that is not a gate verdict propagates immediately.

    id: TST-RP-004
    Given: A synthesizer that raises (e.g. the provider is down)
    When: The loop runs
    Then: The error propagates after a single call, with no retry
    """
    calls = scripted([True], synth_error=RuntimeError("provider down"))
    with pytest.raises(RuntimeError, match="provider down"):
        tdd_machine.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert len(calls["synth"]) == 1
