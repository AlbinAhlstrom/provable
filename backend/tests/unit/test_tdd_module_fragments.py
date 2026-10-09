"""GREEN returns a module fragment (imports + helper classes + target class); failures never poison the domain."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from onboarding.cst_isolator import FragmentError, merge_module_fragment
from onboarding.router_engine import BusinessSpec
from service_layer import tdd_machine as tm

MODULE = '''from dataclasses import dataclass
from typing import Optional


class Marker:
    pass


@dataclass
class Booking:
    id: str = ""
'''


# ── merge_module_fragment ────────────────────────────────────────────────────────────────────────
def test_merge_adds_missing_imports_and_replaces_the_target_class():
    """Verify the model can bring the imports its class needs.

    id: TST-FRG-001
    Given: A module without a datetime import and a fragment that uses datetime
    When: The fragment is merged
    Then: The import is added after the existing imports, the class is replaced, other classes are untouched
    """
    fragment = "from datetime import datetime\n\n@dataclass\nclass Booking:\n    id: str = ''\n    start: Optional[datetime] = None\n"
    out = merge_module_fragment(MODULE, "Booking", fragment)
    assert out.index("from datetime import datetime") < out.index("class Marker")
    assert "start: Optional[datetime] = None" in out and "class Marker" in out
    compile(out, "m", "exec")


def test_merge_does_not_duplicate_existing_imports():
    """Verify an import already present is not added twice.

    id: TST-FRG-002
    Given: A fragment repeating an existing import
    When: It is merged
    Then: The import appears once
    """
    out = merge_module_fragment(MODULE, "Booking", "from typing import Optional\n\n@dataclass\nclass Booking:\n    id: str = ''\n")
    assert out.count("from typing import Optional") == 1


def test_merge_places_helper_exception_before_the_target_and_replaces_existing_helpers():
    """Verify helper classes (e.g. domain exceptions) are kept, ordered before the target, and updated in place.

    id: TST-FRG-003
    Given: A fragment defining an exception class and the target
    When: It is merged twice with a changed exception
    Then: The exception precedes the target, exists once, and reflects the latest definition
    """
    frag = "class InvalidDurationError(Exception):\n    pass\n\n@dataclass\nclass Booking:\n    id: str = ''\n"
    once = merge_module_fragment(MODULE, "Booking", frag)
    assert once.index("class InvalidDurationError") < once.index("class Booking")
    twice = merge_module_fragment(once, "Booking", frag.replace("    pass", '    """changed"""'))
    assert twice.count("class InvalidDurationError") == 1 and "changed" in twice


@pytest.mark.parametrize("fragment,needle", [
    ("def broken(:\n", "not valid Python"),
    ("@dataclass\nclass Other:\n    id: str = ''\n", "class Booking"),
    ("for n in range(3):\n    print(n)\n\n@dataclass\nclass Booking:\n    id: str = ''\n", "at module level"),
    ("X, Y = 1, 2\n\n@dataclass\nclass Booking:\n    id: str = ''\n", "at module level"),
])
def test_merge_rejects_unusable_fragments_loudly(fragment, needle):
    """Verify bad model output raises with a reason instead of silently returning the original source.

    id: TST-FRG-004
    Given: Invalid Python, a missing target class, or module-level code that runs at import (a loop) or cannot be
           told apart by one name (a tuple assignment)
    When: The merge runs
    Then: FragmentError explains what is wrong
    """
    with pytest.raises(FragmentError) as err:
        merge_module_fragment(MODULE, "Booking", fragment)
    assert needle.lower() in str(err.value).lower()


def test_merge_keeps_module_level_helper_functions_and_constants():
    """Verify a helper function or a named constant beside the class is merged, not refused.

    id: TST-FRG-HELPERS
    Given: A fragment with a constant, a helper function and the target class (what a model writes for a lookup
           table or a small pure helper; refusing it cost the code writer its one retry on a formality in three
           of five chess builds)
    When: It is merged, then merged again with both changed
    Then: Both stand before the target class, exist once, and hold the latest definition
    """
    frag = ("STEPS = {'N': 2}\n\n\ndef on_board(n: int) -> bool:\n    return 0 <= n < 8\n\n\n"
            "@dataclass\nclass Booking:\n    id: str = ''\n")
    once = merge_module_fragment(MODULE, "Booking", frag)
    assert once.index("STEPS = ") < once.index("class Booking") and once.index("def on_board") < once.index("class Booking")
    twice = merge_module_fragment(once, "Booking", frag.replace("'N': 2", "'N': 3").replace("n < 8", "n < 9"))
    assert twice.count("STEPS = ") == 1 and "'N': 3" in twice
    assert twice.count("def on_board") == 1 and "n < 9" in twice
    compile(twice, "booking.py", "exec")


# ── RED gate: a broken DOMAIN module is not a broken TEST ────────────────────────────────────────
DOMAIN_BROKEN = {"collectors": [{"outcome": "failed", "longrepr": (
    "tests/unit/test_x.py:4: in <module>\n    from src.domain.booking import Booking\n"
    "src/domain/booking.py:19: in Booking\n    start_time: Optional[datetime] = None\n"
    "E   NameError: name 'datetime' is not defined. Did you forget to import 'datetime'?")}]}


def test_gate_blames_the_domain_module_when_it_does_not_import():
    """Verify a NameError inside src/domain is reported as a domain problem, with the real error line.

    id: TST-FRG-005
    Given: A collection error whose traceback runs through src/domain/booking.py
    When: The RED gate evaluates it
    Then: The status is REJECTED_DOMAIN_BROKEN and the reason names the NameError, not just 'in <module>'
    """
    verdict = tm.evaluate_red_gate_result(2, DOMAIN_BROKEN, "")
    assert verdict["status"] == "REJECTED_DOMAIN_BROKEN" and verdict["approved"] is False
    assert "NameError" in verdict["reason"] and "src/domain/booking.py" in verdict["reason"]


def test_gate_headline_prefers_the_final_error_line_for_broken_tests():
    """Verify the reason shown to the test generator is the actual error, not the first traceback line.

    id: TST-FRG-006
    Given: A collection error in the test module itself
    When: The gate evaluates it
    Then: The reason contains the final 'E ' line
    """
    rep = {"collectors": [{"outcome": "failed", "longrepr": "tests/unit/test_x.py:2: in <module>\n    import nope\nE   ModuleNotFoundError: No module named 'nope'"}]}
    assert "ModuleNotFoundError: No module named 'nope'" in tm.evaluate_red_gate_result(2, rep, "")["reason"]


# ── The loop: rollback, domain-broken, fragment rejection ────────────────────────────────────────
def _spec():
    return BusinessSpec(spec_id="SPEC-F1", title="t", description="d", given_when_then="Given a When b Then c",
                        target_aggregate="Booking", spec_type="DOMAIN_INVARIANT", is_mathematical_boundary=False, priority="High")


GOOD_TEST = "import pytest\n\ndef test_a():\n    assert 1 == 2\n"
GOOD_FRAGMENT = "@dataclass\nclass Booking:\n    id: str = ''\n    extra: int = 1\n"


def _script(monkeypatch, red_status="APPROVED_RED", green_pass=(False, False), fragments=(GOOD_FRAGMENT, GOOD_FRAGMENT)):
    calls = {"red_gen": 0, "synth": [], "feedback": []}
    greens = iter(green_pass)
    frags = iter(fragments)
    runs = {"n": 0}

    def gen(spec, class_source, module_name, class_name, rejection_feedback="", existing_tests="", **_ignored):
        calls["red_gen"] += 1
        return GOOD_TEST

    def synth(extracted_class, target_class_name, spec, failure_output="", test_source="", module_imports="", existing_tests="", **_ignored):
        calls["synth"].append(failure_output)
        return next(frags)

    def run(path, cwd=None, timeout_seconds=5):
        if os.path.isdir(path):  # regression run over tests/unit
            return {"exit_code": 0, "stderr": "", "report": None}
        runs["n"] += 1
        if runs["n"] == 1:
            return {"exit_code": 1, "stderr": "", "report": None}
        return {"exit_code": 0 if next(greens) else 1, "stderr": "", "report": None}

    monkeypatch.setattr(tm, "generate_red_test", gen)
    monkeypatch.setattr(tm, "synthesize_green_class_implementation", synth)
    monkeypatch.setattr(tm, "run_isolated_pytest", run)
    monkeypatch.setattr(tm, "evaluate_red_gate_result",
                        lambda *a, **k: {"approved": red_status == "APPROVED_RED", "status": red_status, "reason": "gate says " + red_status})
    return calls


def _domain_path(tmp_path):
    return tmp_path / "src" / "domain" / "booking.py"


def test_dead_end_rolls_the_domain_file_back(monkeypatch, tmp_path):
    """Verify a failed spec leaves the domain exactly as it found it.

    id: TST-FRG-007
    Given: A GREEN gate that rejects both attempts
    When: The loop dead-ends
    Then: booking.py equals its pre-GREEN content and the result says rolled_back
    """
    _script(monkeypatch)
    (tmp_path / "src" / "domain").mkdir(parents=True)
    original = "from dataclasses import dataclass\n\n@dataclass\nclass Booking:\n    id: str = ''\n"
    _domain_path(tmp_path).write_text(original)
    result = tm.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert result["status"] == "REQUIRES_HUMAN_INTERVENTION" and result["rolled_back"] is True
    assert _domain_path(tmp_path).read_text() == original


def test_success_keeps_the_new_code(monkeypatch, tmp_path):
    """Verify a fulfilled spec keeps its implementation.

    id: TST-FRG-008
    Given: A GREEN gate that approves
    When: The loop runs
    Then: The merged class is in booking.py and nothing is rolled back
    """
    _script(monkeypatch, green_pass=(True,), fragments=(GOOD_FRAGMENT,))
    (tmp_path / "src" / "domain").mkdir(parents=True)
    _domain_path(tmp_path).write_text("from dataclasses import dataclass\n\n@dataclass\nclass Booking:\n    id: str = ''\n")
    result = tm.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert result["status"] == "FULFILLED" and "extra: int = 1" in _domain_path(tmp_path).read_text()


def test_exceptions_also_roll_back(monkeypatch, tmp_path):
    """Verify even an unexpected error cannot leave half-applied code behind.

    id: TST-FRG-009
    Given: A synthesizer that raises after the domain file was read
    When: The loop runs
    Then: The error propagates and booking.py is unchanged
    """
    _script(monkeypatch)
    monkeypatch.setattr(tm, "synthesize_green_class_implementation", lambda **k: (_ for _ in ()).throw(RuntimeError("provider down")))
    (tmp_path / "src" / "domain").mkdir(parents=True)
    original = "from dataclasses import dataclass\n\n@dataclass\nclass Booking:\n    id: str = ''\n"
    _domain_path(tmp_path).write_text(original)
    with pytest.raises(RuntimeError, match="provider down"):
        tm.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert _domain_path(tmp_path).read_text() == original


def test_broken_domain_is_a_dead_end_not_a_test_regeneration(monkeypatch, tmp_path):
    """Verify a domain that cannot import never burns the RED retry on a perfectly good test.

    id: TST-FRG-010
    Given: A RED gate verdict of REJECTED_DOMAIN_BROKEN
    When: The loop runs
    Then: The test is generated once, no GREEN work happens, and the dead end names the domain
    """
    calls = _script(monkeypatch, red_status="REJECTED_DOMAIN_BROKEN")
    result = tm.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert calls["red_gen"] == 1 and calls["synth"] == []
    assert result["phase"] == "RED_GATE" and result["status"] == "REQUIRES_HUMAN_INTERVENTION"
    assert "domain" in result["error"].lower()


def test_unparseable_fragment_consumes_a_green_attempt_and_feeds_back(monkeypatch, tmp_path):
    """Verify invalid model output is a rejection with a reason, not a silent no-op.

    id: TST-FRG-011
    Given: A first fragment that is not valid Python, then a good one that passes
    When: The loop runs
    Then: The retry's feedback carries the parse error and the spec is FULFILLED
    """
    calls = _script(monkeypatch, green_pass=(True,), fragments=("def broken(:\n", GOOD_FRAGMENT))
    result = tm.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert result["status"] == "FULFILLED" and len(result["attempts"]) == 2
    assert "not valid python" in calls["synth"][1].lower()


def test_the_code_writer_is_shown_the_helpers_beside_the_class(monkeypatch, tmp_path):
    """Verify helpers at module level reach the GREEN prompt: shown only the class, the writer cannot use them.

    id: TST-FRG-HELPERS-SHOWN
    Given: A domain module with a helper class, a helper function and a constant beside the target class
    When: A spec goes through the loop
    Then: The code writer was given those three as source, and not the target class a second time
    """
    from onboarding.cst_isolator import module_helpers_source
    source = MODULE + "\n\nLIMIT = 3\n\n\ndef within(n: int) -> bool:\n    return n <= LIMIT\n"
    helpers = module_helpers_source(source, "Booking")
    assert "class Marker" in helpers and "LIMIT = 3" in helpers and "def within" in helpers
    assert "class Booking" not in helpers and "import" not in helpers

    import agent_orchestrator
    seen = {}

    def answer(prompt, **kwargs):
        seen["prompt"] = prompt
        return ""
    monkeypatch.setattr(agent_orchestrator, "call_gemini", answer)
    with pytest.raises(RuntimeError):
        tm.synthesize_green_class_implementation(
            extracted_class="@dataclass\nclass Booking:\n    id: str = ''\n", target_class_name="Booking",
            spec=_spec(), module_helpers=helpers)
    assert "def within(n: int) -> bool:" in seen["prompt"]
