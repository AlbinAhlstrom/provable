"""Each new spec's test and implementation must be written against the already-verified tests of the same class."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import agent_orchestrator
from onboarding.router_engine import BusinessSpec
from service_layer import tdd_machine as tm


def _spec():
    return BusinessSpec(spec_id="SPEC-X3", title="t", description="d", given_when_then="Given a When b Then c",
                        target_aggregate="ClientInquiry", spec_type="DOMAIN_INVARIANT", is_mathematical_boundary=False, priority="High")


def _write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def test_collects_only_other_verified_tests_for_the_same_module(tmp_path):
    """Verify the context is exactly the other verified tests that exercise this class.

    id: TST-CTX-001
    Given: Verified tests for this module, for another module, the skeleton test and the spec's own test file
    When: collect_existing_tests runs
    Then: Only the other tests for this module are returned
    """
    unit = tmp_path / "tests" / "unit"
    _write(unit / "test_spec_001.py", "from src.domain.client_inquiry import ClientInquiry\ndef test_one():\n    assert 'submitted'\n")
    _write(unit / "test_spec_002.py", "from src.domain.babysitter_profile import BabysitterProfile\ndef test_two():\n    pass\n")
    _write(unit / "test_skeleton.py", "from src.domain.client_inquiry import ClientInquiry\ndef test_skel():\n    pass\n")
    _write(unit / "test_spec_x3.py", "from src.domain.client_inquiry import ClientInquiry\ndef test_own():\n    pass\n")
    text = tm.collect_existing_tests(str(unit), exclude=str(unit / "test_spec_x3.py"), module_name="client_inquiry")
    assert "test_one" in text and "test_two" not in text and "test_skel" not in text and "test_own" not in text
    assert tm.collect_existing_tests(str(unit), exclude="", module_name="nope") == ""


def test_collection_is_capped(tmp_path):
    """Verify context cannot grow without bound as specs accumulate.

    id: TST-CTX-002
    Given: Many large verified tests
    When: collect_existing_tests runs with a limit
    Then: The text is truncated to the limit
    """
    unit = tmp_path / "tests" / "unit"
    for i in range(6):
        _write(unit / f"test_spec_{i:03d}.py", "from src.domain.m import C\n" + "# filler\n" * 400)
    assert len(tm.collect_existing_tests(str(unit), exclude="", module_name="m", limit=1500)) <= 1600


def test_red_and_green_prompts_include_the_existing_tests(monkeypatch):
    """Verify both generators see the verified tests they must stay consistent with.

    id: TST-CTX-003
    Given: A block of existing verified tests
    When: The RED prompt and the GREEN prompt are built
    Then: Each contains it, under a heading that tells the model to stay consistent
    """
    seen = {}
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage="general", **_: seen.setdefault(stage, prompt) and (
        "```python\nimport pytest\n\ndef test_a():\n    assert 1 == 2\n```" if stage == "red_test_generation" else "```python\n@dataclass\nclass ClientInquiry:\n    id: str = ''\n```"))
    marker = "def test_marker_existing_behavior():"
    tm.generate_red_test(_spec(), "class ClientInquiry:\n    pass\n", "client_inquiry", "ClientInquiry", existing_tests=marker)
    tm.synthesize_green_class_implementation("@dataclass\nclass ClientInquiry:\n    id: str = ''\n", "ClientInquiry", _spec(), existing_tests=marker)
    assert marker in seen["red_test_generation"] and "consistent" in seen["red_test_generation"].lower()
    assert marker in seen["green_code_repair"] and "keep passing" in seen["green_code_repair"].lower()


def test_loop_passes_the_existing_tests_to_both_generators(monkeypatch, tmp_path):
    """Verify the loop wires the collected context through.

    id: TST-CTX-004
    Given: A verified test for the same module already on disk
    When: The loop runs
    Then: generate_red_test and synthesize_green_class_implementation both receive it
    """
    unit = tmp_path / "tests" / "unit"
    _write(unit / "test_spec_001.py", "from src.domain.client_inquiry import ClientInquiry\ndef test_prior_behavior():\n    pass\n")
    got = {}
    n = {"i": 0}

    def gen(spec, class_source, module_name, class_name, rejection_feedback="", existing_tests=""):
        got["red"] = existing_tests
        return "import pytest\n\ndef test_a():\n    assert 1 == 2\n"

    def synth(extracted_class, target_class_name, spec, failure_output="", test_source="", module_imports="", existing_tests=""):
        got["green"] = existing_tests
        return "@dataclass\nclass ClientInquiry:\n    id: str = ''\n"

    def run(path, cwd=None, timeout_seconds=5):
        if os.path.isdir(path):
            return {"exit_code": 0, "stderr": "", "report": None}
        n["i"] += 1
        return {"exit_code": 1 if n["i"] == 1 else 0, "stderr": "", "report": None}

    monkeypatch.setattr(tm, "generate_red_test", gen)
    monkeypatch.setattr(tm, "synthesize_green_class_implementation", synth)
    monkeypatch.setattr(tm, "run_isolated_pytest", run)
    monkeypatch.setattr(tm, "evaluate_red_gate_result", lambda *a, **k: {"approved": True, "status": "APPROVED_RED", "reason": "ok"})
    tm.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert "test_prior_behavior" in got["red"] and "test_prior_behavior" in got["green"]
