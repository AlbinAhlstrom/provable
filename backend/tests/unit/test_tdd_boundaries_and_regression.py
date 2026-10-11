"""Boundary specs need both sides tested; a new implementation must not break earlier specs; failed specs are quarantined."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from onboarding.router_engine import BusinessSpec
from service_layer import tdd_machine as tm

ONE_TEST = "import pytest\n\ndef test_a():\n    assert 1 == 2\n"
TWO_TESTS = "import pytest\n\ndef test_reject_below():\n    assert 1 == 2\n\ndef test_accept_at_boundary():\n    assert 2 == 3\n"
PARAMETRIZED = ("import pytest\n\n@pytest.mark.parametrize('n,ok', [(119, False), (120, True)])\n"
                "def test_boundary(n, ok):\n    assert (n >= 120) == ok\n")


# ── A. Both sides of a boundary ──────────────────────────────────────────────────────────────────
def test_lint_requires_two_cases_for_boundary_specs():
    """Verify a boundary spec cannot be satisfied by testing only one side.

    id: TST-BND-001
    Given: A spec flagged as a mathematical boundary
    When: lint_red_test runs with require_both_sides=True
    Then: One test function is refused, while two tests or a parametrized test are accepted
    """
    ok, reason = tm.lint_red_test(ONE_TEST, require_both_sides=True)
    assert ok is False and "both sides" in reason.lower()
    assert tm.lint_red_test(TWO_TESTS, require_both_sides=True) == (True, "")
    assert tm.lint_red_test(PARAMETRIZED, require_both_sides=True) == (True, "")
    assert tm.lint_red_test(ONE_TEST, require_both_sides=False) == (True, "")


def test_red_prompt_demands_both_sides_of_the_boundary():
    """Verify the instructions to the test writer name both the rejected and the accepted side.

    id: TST-BND-002
    Given: The red_test_generation prompt
    When: Its text is read
    Then: It requires a case just beyond the boundary and a case exactly at it
    """
    text = open(os.path.join(os.path.dirname(tm.__file__), "..", "prompts", "red_test_generation.md"), encoding="utf-8").read().lower()
    assert "both sides" in text and "exactly at" in text


def _spec(boundary):
    return BusinessSpec(spec_id="SPEC-B1", title="t", description="d", given_when_then="Given a When b Then c",
                        target_aggregate="Booking", spec_type="DOMAIN_INVARIANT", is_mathematical_boundary=boundary, priority="High")


def _wire(monkeypatch, tests, run):
    gens = iter(tests)
    seen = {"prompts": []}
    monkeypatch.setattr(tm, "generate_red_test", lambda spec, cls, mod, name, rejection_feedback="", existing_tests="", **_ignored: seen["prompts"].append(rejection_feedback) or next(gens))
    monkeypatch.setattr(tm, "synthesize_green_class_implementation", lambda **k: "@dataclass\nclass Booking:\n    id: str = ''\n")
    monkeypatch.setattr(tm, "run_isolated_pytest", run)
    monkeypatch.setattr(tm, "evaluate_red_gate_result", lambda *a, **k: {"approved": True, "status": "APPROVED_RED", "reason": "ok"})
    return seen


def test_boundary_spec_with_a_one_sided_test_is_bounced_back_once(monkeypatch, tmp_path):
    """Verify the loop enforces two-sided tests for boundary specs through the single RED retry.

    id: TST-BND-003
    Given: A boundary spec whose first generated test covers one side only
    When: The loop runs
    Then: The test is regenerated once with the 'both sides' reason, and the two-sided test is used
    """
    state = {"n": 0}

    def run(path, cwd=None, timeout_seconds=5):
        state["n"] += 1
        return {"exit_code": 1 if state["n"] == 1 else 0, "stderr": "", "report": None}

    seen = _wire(monkeypatch, [ONE_TEST, TWO_TESTS], run)
    result = tm.execute_spec_tdd_loop(_spec(True), str(tmp_path))
    assert result["status"] == "FULFILLED" and len(seen["prompts"]) == 2 and "both sides" in seen["prompts"][1].lower()
    assert "def test_a():" in seen["prompts"][1]  # the writer gets its refused test back, to keep what was right in it
    assert (tmp_path / "tests" / "unit" / "test_spec_b1.py").read_text() == TWO_TESTS


def test_the_test_writer_is_told_when_a_spec_states_a_limit(monkeypatch):
    """Verify the writer knows beforehand what the lint will ask of it.

    id: TST-BND-006
    Given: A spec marked as stating a limit, and one that is not
    When: The test prompt is built for each
    Then: Only the first says the spec states a limit and that both sides are required
    """
    import agent_orchestrator
    prompts = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda p, stage="general", **k: prompts.append(p) or "```python\nx\n```")
    for boundary in (True, False):
        tm.generate_red_test(_spec(boundary), "class Booking:\n    pass\n", "booking", "Booking")
    assert "States a limit" in prompts[0] and "States a limit" not in prompts[1]


# ── B. Regression gate and quarantine ────────────────────────────────────────────────────────────
def _report_with_failures(*names):
    return {"tests": [{"nodeid": f"tests/unit/{n}.py::test_x", "call": {"outcome": "failed", "crash": {"message": "AssertionError: x"}, "longrepr": "E   AssertionError: x"}} for n in names]}


def test_new_spec_that_breaks_an_earlier_spec_is_rejected_with_the_names(monkeypatch, tmp_path):
    """Verify a regression is a GREEN rejection that tells the generator which earlier tests broke.

    id: TST-BND-004
    Given: A new test that passes but an earlier spec's test that now fails in the full unit run
    When: The loop runs with a retry that fixes it
    Then: The first attempt is rejected as a regression naming the file, and the retry is fulfilled
    """
    calls = {"n": 0, "feedback": []}

    def run(path, cwd=None, timeout_seconds=5):
        calls["n"] += 1
        if os.path.isdir(path):  # the regression run over tests/unit
            regressions = calls.setdefault("reg", iter([_report_with_failures("test_spec_old"), None]))
            report = next(regressions)
            return {"exit_code": 1 if report else 0, "stderr": "", "report": report}
        return {"exit_code": 1 if calls["n"] == 1 else 0, "stderr": "", "report": None}

    _wire(monkeypatch, [TWO_TESTS], run)
    real_synth = tm.synthesize_green_class_implementation
    monkeypatch.setattr(tm, "synthesize_green_class_implementation",
                        lambda **k: calls["feedback"].append(k["failure_output"]) or "@dataclass\nclass Booking:\n    id: str = ''\n")
    result = tm.execute_spec_tdd_loop(_spec(False), str(tmp_path))
    assert result["status"] == "FULFILLED" and len(result["attempts"]) == 2
    assert result["attempts"][0]["approved"] is False and "regression" in result["attempts"][0]["reason"].lower()
    assert "test_spec_old" in calls["feedback"][1]


def test_failed_green_moves_its_test_to_pending_so_it_cannot_break_later_specs(monkeypatch, tmp_path):
    """Verify a dead-ended spec's unverified test is quarantined, not left in the regression suite.

    id: TST-BND-005
    Given: A GREEN gate that rejects twice
    When: The loop dead-ends
    Then: The test file is gone from tests/unit and kept under tests/pending for a human
    """
    def run(path, cwd=None, timeout_seconds=5):
        return {"exit_code": 1, "stderr": "", "report": None}

    _wire(monkeypatch, [TWO_TESTS], run)
    result = tm.execute_spec_tdd_loop(_spec(False), str(tmp_path))
    assert result["status"] == "REQUIRES_HUMAN_INTERVENTION"
    assert not (tmp_path / "tests" / "unit" / "test_spec_b1.py").exists()
    assert (tmp_path / "tests" / "pending" / "test_spec_b1.py").read_text() == TWO_TESTS
    assert result["pending_test"].endswith(os.path.join("tests", "pending", "test_spec_b1.py"))


def test_red_dead_end_deletes_the_broken_test(monkeypatch, tmp_path):
    """Verify a test rejected twice at RED is removed, since it is known to be broken.

    id: TST-BND-006
    Given: A RED gate that rejects both generated tests
    When: The loop dead-ends at RED
    Then: No test file for the spec remains in tests/unit
    """
    def run(path, cwd=None, timeout_seconds=5):
        return {"exit_code": 1, "stderr": "", "report": None}

    _wire(monkeypatch, [TWO_TESTS, TWO_TESTS], run)
    monkeypatch.setattr(tm, "evaluate_red_gate_result", lambda *a, **k: {"approved": False, "status": "REJECTED_SYNTAX_OR_EXEC", "reason": "broken"})
    result = tm.execute_spec_tdd_loop(_spec(False), str(tmp_path))
    assert result["phase"] == "RED_GATE" and not (tmp_path / "tests" / "unit" / "test_spec_b1.py").exists()


def test_a_refusal_named_like_a_python_error_is_not_a_broken_test():
    """Verify the RED gate reads an error's name whole: a product's refusal may end in the name of a Python error.

    id: TST-RED-GATE-ERROR-NAME
    Given: A test that expects the refusal `EmptyNameError` and fails because the method does not exist yet, and a
           test that uses a name it never defined
    When: The RED gate judges each
    Then: The first is a valid RED, the second a broken test
    """
    from service_layer.tdd_machine import evaluate_red_gate_result

    def judged(message):
        return evaluate_red_gate_result(exit_code=1, report_json={
            "summary": {"failed": 1}, "tests": [{"call": {"crash": {"message": message}}}]})

    assert judged("AssertionError: assert 'AttributeError' == 'EmptyNameError'")["approved"] is True
    broken = judged("NameError: name 'build_two_items' is not defined")
    assert broken["approved"] is False and broken["status"] == "REJECTED_SYNTAX_OR_EXEC"
