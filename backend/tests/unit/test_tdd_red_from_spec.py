"""RED tests must come from the BDD spec, be gated for the RIGHT failure, and be shown to the GREEN step."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from onboarding.router_engine import BusinessSpec
from service_layer import tdd_machine as tm


def _report(message, longrepr=""):
    return {"tests": [{"nodeid": "t::x", "call": {"outcome": "failed", "crash": {"message": message}, "longrepr": longrepr or message}}]}


def _spec():
    return BusinessSpec(spec_id="SPEC-R1", title="Minimum Booking Duration", description="Bookings last at least 2 hours.",
                        given_when_then="Given a 30 minute booking When it is validated Then InvalidDurationException is raised",
                        target_aggregate="Booking", spec_type="DOMAIN_INVARIANT", is_mathematical_boundary=False, priority="High")


# ── RED gate: only the right kind of failure counts as RED ──────────────────────────────────────
@pytest.mark.parametrize("message", [
    "AssertionError: assert 0.5 >= 2.0",
    "Failed: DID NOT RAISE <class 'Exception'>",
    "AttributeError: 'Booking' object has no attribute 'validate_duration'",
    "TypeError: Booking.validate_duration() got an unexpected keyword argument 'now'",
])
def test_red_gate_accepts_behavioral_failures(message):
    """Verify failures that show missing/incorrect behavior are valid RED.

    id: TST-RFS-001
    Given: A failing test whose crash is an assertion, missing raise, missing method or method signature mismatch
    When: The RED gate evaluates it
    Then: It is approved
    """
    assert tm.evaluate_red_gate_result(1, _report(message), "")["approved"] is True


@pytest.mark.parametrize("message", [
    "TypeError: Booking.__init__() got an unexpected keyword argument 'id'",
    "TypeError: Booking.__init__() missing 1 required positional argument: 'booking_id'",
    "ImportError: cannot import name 'InvalidDurationException' from 'src.domain.booking'",
    "NameError: name 'datetime' is not defined",
    "ModuleNotFoundError: No module named 'src.domain.nope'",
    "SyntaxError: invalid syntax",
])
def test_red_gate_rejects_broken_tests(message):
    """Verify a test that cannot even run correctly is not accepted as RED.

    id: TST-RFS-002
    Given: A failing test whose crash is a constructor misuse, import/name error or syntax error
    When: The RED gate evaluates it
    Then: It is rejected, with the reason fed back for the single retry
    """
    verdict = tm.evaluate_red_gate_result(1, _report(message), "")
    assert verdict["approved"] is False and message.split(":")[0].lower() in verdict["reason"].lower()


def test_red_gate_still_rejects_tautologies():
    """Verify a test that already passes is rejected.

    id: TST-RFS-003
    Given: Exit code 0 in the RED phase
    When: The gate evaluates it
    Then: It is rejected as a tautology
    """
    assert tm.evaluate_red_gate_result(0, None, "")["status"] == "REJECTED_TAUTOLOGY"


# ── Test lint ────────────────────────────────────────────────────────────────────────────────────
def test_lint_rejects_existence_checks_and_accepts_behavioral_tests():
    """Verify hasattr-style tests are refused before they are ever run.

    id: TST-RFS-004
    Given: A hasattr-based test and a behavioral test
    When: lint_red_test inspects them
    Then: The first is rejected with a reason and the second accepted
    """
    bad = "def test_x():\n    assert hasattr(object(), 'validate_invariants')\n"
    good = ("import pytest\n\ndef test_x():\n    with pytest.raises(Exception) as e:\n        raise ValueError('x')\n"
            "    assert type(e.value).__name__ == 'ValueError'\n")
    assert tm.lint_red_test(bad)[0] is False and "hasattr" in tm.lint_red_test(bad)[1]
    assert tm.lint_red_test(good) == (True, "")
    assert tm.lint_red_test("def test_x(:\n")[0] is False
    assert tm.lint_red_test("x = 1\n")[0] is False


# ── Prompts ──────────────────────────────────────────────────────────────────────────────────────
def test_red_prompt_contains_the_spec_and_the_class_api(monkeypatch):
    """Verify the test generator sees the scenario and the real constructor, not a template.

    id: TST-RFS-005
    Given: A spec and the current class source
    When: generate_red_test builds its prompt
    Then: The prompt includes the Given/When/Then, the import line and the class fields, and the fenced reply is unwrapped
    """
    import agent_orchestrator
    seen = {}

    def fake(prompt, stage="general", **_):
        seen["prompt"], seen["stage"] = prompt, stage
        return "```python\nimport pytest\n\ndef test_a():\n    assert 1 == 2\n```"

    monkeypatch.setattr(agent_orchestrator, "call_gemini", fake)
    code = tm.generate_red_test(_spec(), "@dataclass\nclass Booking:\n    booking_id: str\n    start_time: str = ''\n", "booking", "Booking")
    assert seen["stage"] == "red_test_generation"
    for needle in ("30 minute booking", "from src.domain.booking import Booking", "booking_id: str"):
        assert needle in seen["prompt"]
    assert code.startswith("import pytest") and "```" not in code


def test_red_prompt_carries_rejection_feedback_on_the_retry(monkeypatch):
    """Verify the one RED retry is told why the previous test was rejected.

    id: TST-RFS-006
    Given: A rejection reason from the gate
    When: generate_red_test is called with it
    Then: The prompt contains that reason
    """
    import agent_orchestrator
    seen = {}
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda p, stage="general", **_: seen.setdefault("p", p) or "def test_a():\n    assert False\n")
    tm.generate_red_test(_spec(), "class Booking:\n    pass\n", "booking", "Booking", rejection_feedback="constructor got unexpected keyword 'id'")
    assert "constructor got unexpected keyword 'id'" in seen["p"]


def test_green_prompt_shows_the_frozen_test(monkeypatch):
    """Verify the GREEN generator receives the test source it must satisfy.

    id: TST-RFS-007
    Given: A frozen RED test
    When: synthesize_green_class_implementation builds its prompt
    Then: The test source is in the prompt
    """
    import agent_orchestrator
    seen = {}

    def fake(prompt, stage="general", **_):
        seen["prompt"] = prompt
        return "```python\n@dataclass\nclass Booking:\n    booking_id: str = ''\n```"

    monkeypatch.setattr(agent_orchestrator, "call_gemini", fake)
    tm.synthesize_green_class_implementation("@dataclass\nclass Booking:\n    booking_id: str = ''\n", "Booking", _spec(),
                                            failure_output="AssertionError", test_source="def test_marker_xyz():\n    assert False\n")
    assert "test_marker_xyz" in seen["prompt"]


def test_green_synthesis_fails_loudly_instead_of_faking_an_implementation(monkeypatch):
    """Verify an empty/invalid LLM answer is an error, never a silently injected stub.

    id: TST-RFS-008
    Given: An LLM that returns nothing usable (e.g. the provider is down)
    When: GREEN synthesis runs
    Then: It raises, so the spec cannot be FULFILLED by a hardcoded validate_invariants() -> True
    """
    import agent_orchestrator
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda *a, **k: "")
    monkeypatch.setattr(agent_orchestrator, "LAST_LLM_ERROR", "429 quota exceeded", raising=False)
    with pytest.raises(RuntimeError, match="429 quota exceeded"):
        tm.synthesize_green_class_implementation("@dataclass\nclass Booking:\n    pass\n", "Booking", _spec())


# ── The loop: RED retry policy ───────────────────────────────────────────────────────────────────
class _Script:
    def __init__(self, monkeypatch, red_tests, red_exit_codes, green_ok=True):
        self.red_prompts, self.generated = [], []
        tests = iter(red_tests)
        exits = iter(red_exit_codes)

        def fake_gen(spec, class_source, module_name, class_name, rejection_feedback="", existing_tests="", **_ignored):
            self.red_prompts.append(rejection_feedback)
            return next(tests)

        def fake_run(path, cwd=None):
            code = next(exits)
            return {"exit_code": code, "stderr": "", "report": _report("TypeError: Booking.__init__() got an unexpected keyword argument 'id'") if code == 99 else _report("AssertionError: x")}

        monkeypatch.setattr(tm, "generate_red_test", fake_gen)
        monkeypatch.setattr(tm, "synthesize_green_class_implementation", lambda **k: "@dataclass\nclass Booking:\n    id: str = ''\n")
        runs = {"n": 0}

        def run(path, cwd=None, timeout_seconds=5):
            if os.path.isdir(path):  # regression run over tests/unit
                return {"exit_code": 0, "stderr": "", "report": None}
            runs["n"] += 1
            if runs["n"] <= self.red_runs:
                r = fake_run(path, cwd)
                r["exit_code"] = 1
                return r
            return {"exit_code": 0 if green_ok else 1, "stderr": "", "report": None}

        self.red_runs = len(red_exit_codes)
        self._codes = red_exit_codes
        monkeypatch.setattr(tm, "run_isolated_pytest", run)
        # scripted RED verdicts: 99 => constructor bug (rejected), anything else => behavioral failure (approved)
        original = tm.evaluate_red_gate_result
        seq = iter(red_exit_codes)

        def gate(exit_code, report=None, stderr=""):
            code = next(seq)
            return {"approved": False, "status": "REJECTED_SYNTAX_OR_EXEC", "reason": "TypeError in __init__"} if code == 99 else {"approved": True, "status": "APPROVED_RED", "reason": "ok"}

        monkeypatch.setattr(tm, "evaluate_red_gate_result", gate)


GOOD = "import pytest\n\ndef test_a():\n    assert 1 == 2\n"


def test_loop_uses_the_generated_test_and_retries_red_once(monkeypatch, tmp_path):
    """Verify a rejected RED test gets one regeneration with the rejection as feedback.

    id: TST-RFS-009
    Given: A first generated test rejected by the RED gate and a good second one
    When: The loop runs
    Then: generate_red_test is called twice, the second time with the rejection reason, and the spec is FULFILLED
    """
    s = _Script(monkeypatch, [GOOD, GOOD], [99, 1])
    result = tm.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert result["status"] == "FULFILLED"
    assert len(s.red_prompts) == 2 and s.red_prompts[0] == "" and "TypeError in __init__" in s.red_prompts[1]
    written = (tmp_path / "tests" / "unit" / "test_spec_r1.py").read_text()
    assert written == GOOD


def test_loop_never_regenerates_red_a_third_time(monkeypatch, tmp_path):
    """Verify two rejected RED tests end in a visible dead end before any GREEN work.

    id: TST-RFS-010
    Given: Two consecutive rejected RED tests
    When: The loop runs
    Then: There are exactly two generations, no GREEN call, and status REQUIRES_HUMAN_INTERVENTION at RED_GATE
    """
    s = _Script(monkeypatch, [GOOD, GOOD, GOOD], [99, 99, 99])
    result = tm.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert len(s.red_prompts) == 2
    assert result["success"] is False and result["status"] == "REQUIRES_HUMAN_INTERVENTION" and result["phase"] == "RED_GATE"


def test_lint_failure_counts_as_the_red_retry(monkeypatch, tmp_path):
    """Verify a hasattr-style generated test is bounced back to the generator once.

    id: TST-RFS-011
    Given: A first generated test that only checks hasattr, then a behavioral one
    When: The loop runs
    Then: The first never reaches pytest, the second does, and the retry prompt mentions hasattr
    """
    s = _Script(monkeypatch, ["def test_a():\n    assert hasattr(object(), 'x')\n", GOOD], [1])
    result = tm.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert result["status"] == "FULFILLED" and "hasattr" in s.red_prompts[1]


def test_the_test_writer_is_told_to_arrange_the_state_directly_and_show_its_working():
    """Verify the RED prompt asks for a minimal, directly arranged Given and a worked-out expectation.

    id: TST-RED-ARRANGE
    Given: The RED test prompt (replayed on a correct chess class, two of eight tests had a wrong expectation: each
           reached its position through a move sequence the writer mis-tracked; with this guidance, one of 24)
    When: It is read
    Then: It tells the writer to set the fields to the scenario's situation, and to work out each expected result
          in a comment above the assertion
    """
    import agent_orchestrator
    path = os.path.join(os.path.dirname(agent_orchestrator.__file__), "prompts", "red_test_generation.md")
    prompt = open(path, encoding="utf-8").read()
    assert "## Arranging the Given" in prompt and "by setting its fields" in prompt
    assert "works out the expected result" in prompt


def test_a_scenario_about_what_follows_is_acted_out_through_a_method_the_application_calls():
    """Verify the RED prompt has a consequence tested through the promised method that causes it.

    id: TST-RED-CONSEQUENCE
    Given: The RED test prompt (a rule read "when the result is recorded, the score equals the time"; no promised
           method records a result, so the writer named one of its own, it was implemented and passed its test, and
           the application never called it: a won round kept a score of zero)
    When: It is read
    Then: It says the application calls no other method, and that a When which follows from what someone does is
          acted out through the promised method that brings it about
    """
    import agent_orchestrator
    path = os.path.join(os.path.dirname(agent_orchestrator.__file__), "prompts", "red_test_generation.md")
    prompt = open(path, encoding="utf-8").read()
    assert "The application calls no other method of this class" in prompt
    assert "act it out through the listed method that brings it about" in prompt
    assert "If the scenario is not about any of them, name the method you need as the scenario implies." not in prompt


def test_the_test_writer_is_given_the_situation_the_rule_starts_from(monkeypatch):
    """Verify a rule's starting state is not left to its test writer to make up: the contract's situation is shown.

    id: TST-RFS-SITUATION
    Given: A spec that carries the situation its Given names, and one that carries none
    When: generate_red_test builds its prompt for each
    Then: The first prompt shows the situation with its values; the second has no line for one
    """
    import agent_orchestrator
    seen = []
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda p, stage="general", **_: seen.append(p) or "def test_a():\n    assert False\n")
    placed = _spec().model_copy(update={"situation": "`short_booking`: a booking of half an hour: start 10:00, end 10:30"})

    tm.generate_red_test(placed, "class Booking:\n    pass\n", "booking", "Booking")
    tm.generate_red_test(_spec(), "class Booking:\n    pass\n", "booking", "Booking")

    assert "- **Situation** `short_booking`: a booking of half an hour: start 10:00, end 10:30" in seen[0]
    assert "**Situation**" not in seen[1]
