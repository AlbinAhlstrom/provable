"""Generated tests are reviewable per spec; each LLM stage may use its own model; interval rules get an edge case."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
import agent_orchestrator
from onboarding.router_engine import BusinessSpec
from service_layer import services, tdd_machine as tm
from service_layer.unit_of_work import FakeUnitOfWork

_REAL_CALL_GEMINI = agent_orchestrator.call_gemini
TEST_SRC = "import pytest\n\ndef test_a():\n    assert 1 == 2\n\ndef test_b():\n    assert 2 == 3\n"


def _spec(boundary=False):
    return BusinessSpec(spec_id="SPEC-V1", title="t", description="d", given_when_then="Given a When b Then c",
                        target_aggregate="Booking", spec_type="DOMAIN_INVARIANT", is_mathematical_boundary=boundary, priority="High")


# ── per-stage model override ─────────────────────────────────────────────────────────────────────
class _Rec:
    def __init__(self):
        self.kwargs = None

    def create(self, **kwargs):
        self.kwargs = kwargs
        msg = type("M", (), {"content": "ok"})()
        return type("R", (), {"choices": [type("C", (), {"message": msg})()]})()


def _client(rec):
    class C:
        def __init__(self, **_):
            self.chat = type("Chat", (), {"completions": rec})()
    return C


def test_each_stage_can_use_its_own_model(monkeypatch):
    """Verify tests can be written by a different model than the code.

    id: TST-REV-001
    Given: LLM_MODEL set globally and LLM_MODEL_RED_TEST_GENERATION set for one stage
    When: call_gemini runs for that stage and for another
    Then: The stage override applies only to its stage
    """
    rec = _Rec()
    monkeypatch.setattr(agent_orchestrator, "OpenAI", _client(rec))
    monkeypatch.setenv("GEMINI_API_KEY", "k" * 20)
    monkeypatch.setenv("LLM_MODEL", "base-model")
    monkeypatch.setenv("LLM_MODEL_RED_TEST_GENERATION", "test-writer-model")
    _REAL_CALL_GEMINI("p", stage="red_test_generation")
    assert rec.kwargs["model"] == "test-writer-model"
    _REAL_CALL_GEMINI("p", stage="green_code_repair")
    assert rec.kwargs["model"] == "base-model"


# ── the loop returns the generated test in every outcome ─────────────────────────────────────────
def _wire(monkeypatch, red_ok=True, green_ok=True):
    monkeypatch.setattr(tm, "generate_red_test", lambda *a, **k: TEST_SRC)
    monkeypatch.setattr(tm, "synthesize_green_class_implementation", lambda **k: "@dataclass\nclass Booking:\n    id: str = ''\n")
    n = {"i": 0}

    def run(path, cwd=None, timeout_seconds=5):
        if os.path.isdir(path):
            return {"exit_code": 0, "stderr": "", "report": None}
        n["i"] += 1
        return {"exit_code": 1 if n["i"] == 1 else (0 if green_ok else 1), "stderr": "", "report": None}

    monkeypatch.setattr(tm, "run_isolated_pytest", run)
    monkeypatch.setattr(tm, "evaluate_red_gate_result",
                        lambda *a, **k: {"approved": red_ok, "status": "APPROVED_RED" if red_ok else "REJECTED_SYNTAX_OR_EXEC", "reason": "r"})


@pytest.mark.parametrize("red_ok,green_ok", [(True, True), (True, False), (False, True)])
def test_result_always_carries_the_generated_test(monkeypatch, tmp_path, red_ok, green_ok):
    """Verify success, GREEN dead end and RED dead end all expose the test for review.

    id: TST-REV-002
    Given: Each loop outcome
    When: The loop returns
    Then: test_source holds the generated test
    """
    _wire(monkeypatch, red_ok, green_ok)
    result = tm.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert result["test_source"] == TEST_SRC


# ── the service stores a reviewable summary on the spec ──────────────────────────────────────────
def test_execute_inbox_spec_stores_the_tdd_summary_on_the_spec(monkeypatch):
    """Verify the Studio can read the generated test and attempt history from the spec.

    id: TST-REV-003
    Given: A spec in the inbox and a TDD result with attempts and a test
    When: execute_inbox_spec_tdd finishes
    Then: The stored spec has status plus a tdd summary (test source, attempts, error, rollback info)
    """
    uow = FakeUnitOfWork()
    services.add_inbox_spec(_spec(), uow=uow)
    fake_result = {"success": False, "status": "REQUIRES_HUMAN_INTERVENTION", "phase": "DEAD_END", "spec_id": "SPEC-V1",
                   "error": "Regression: x", "test_source": TEST_SRC, "red_attempts": [{"attempt": 1, "approved": True, "reason": "ok"}],
                   "attempts": [{"attempt": 1, "approved": False, "reason": "boom"}], "rolled_back": True, "pending_test": "/w/tests/pending/t.py"}
    monkeypatch.setattr("service_layer.tdd_machine.execute_spec_tdd_loop", lambda spec, workspace_dir: fake_result)
    services.execute_inbox_spec_tdd("SPEC-V1", uow=uow, workspace_dir="/nonexistent")
    stored = next(s for s in services.get_inbox_specs(uow=uow) if s["spec_id"] == "SPEC-V1")
    assert stored["status"] == "REQUIRES_HUMAN_INTERVENTION"
    tdd = stored["tdd"]
    assert tdd["test_source"] == TEST_SRC and tdd["error"] == "Regression: x" and tdd["rolled_back"] is True
    assert tdd["attempts"][0]["reason"] == "boom" and tdd["red_attempts"][0]["approved"] is True
    assert tdd["test_location"] == "tests/pending"


# ── prompt: touching intervals ───────────────────────────────────────────────────────────────────
def test_red_prompt_asks_for_the_touching_interval_case():
    """Verify range/overlap rules get their classic edge case.

    id: TST-REV-004
    Given: The red_test_generation prompt
    When: Its text is read
    Then: It tells the writer to test intervals that merely touch at an endpoint
    """
    text = open(os.path.join(os.path.dirname(tm.__file__), "..", "prompts", "red_test_generation.md"), encoding="utf-8").read().lower()
    assert "touch" in text and "overlap" in text
