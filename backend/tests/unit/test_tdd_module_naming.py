"""The TDD loop must implement behavior in the SAME module the skeleton, routers and repositories import."""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import pytest
from onboarding.router_engine import BusinessSpec
from onboarding.skeleton_builder import to_snake_case
from service_layer import tdd_machine as tm


@pytest.mark.parametrize("name,expected", [
    ("ClientInquiry", "client_inquiry"), ("BabysitterProfile", "babysitter_profile"),
    ("Booking", "booking"), ("ServiceOffering", "service_offering"), ("FAQItem", "faq_item"),
])
def test_snake_case_is_public_and_matches_the_skeleton(name, expected):
    """Verify one naming function is shared by the skeleton and the TDD loop.

    id: TST-NAM-001
    Given: CamelCase aggregate names
    When: to_snake_case is applied
    Then: The module names match what the skeleton generates
    """
    assert to_snake_case(name) == expected


def _spec():
    return BusinessSpec(spec_id="SPEC-N1", title="t", description="d", given_when_then="Given a When b Then c",
                        target_aggregate="ClientInquiry", spec_type="DOMAIN_INVARIANT", is_mathematical_boundary=False, priority="High")


def test_loop_merges_into_the_skeleton_module_not_a_lowercase_twin(monkeypatch, tmp_path):
    """Verify no duplicate module is created and the test imports the real one.

    id: TST-NAM-002
    Given: A skeleton module client_inquiry.py containing ClientInquiry
    When: The loop implements a spec for ClientInquiry
    Then: The merged code is in client_inquiry.py, no clientinquiry.py exists, and the generator was told module client_inquiry
    """
    domain = tmp_path / "src" / "domain"
    domain.mkdir(parents=True)
    skeleton = "from dataclasses import dataclass\n\n@dataclass\nclass ClientInquiry:\n    id: str\n    email: str = ''\n"
    (domain / "client_inquiry.py").write_text(skeleton)
    seen = {}

    def gen(spec, class_source, module_name, class_name, rejection_feedback=""):
        seen["module"], seen["source"] = module_name, class_source
        return "import pytest\n\ndef test_a():\n    assert 1 == 2\n"

    n = {"i": 0}

    def run(path, cwd=None, timeout_seconds=5):
        if os.path.isdir(path):
            return {"exit_code": 0, "stderr": "", "report": None}
        n["i"] += 1
        return {"exit_code": 1 if n["i"] == 1 else 0, "stderr": "", "report": None}

    monkeypatch.setattr(tm, "generate_red_test", gen)
    monkeypatch.setattr(tm, "run_isolated_pytest", run)
    monkeypatch.setattr(tm, "evaluate_red_gate_result", lambda *a, **k: {"approved": True, "status": "APPROVED_RED", "reason": "ok"})
    monkeypatch.setattr(tm, "synthesize_green_class_implementation",
                        lambda **k: "@dataclass\nclass ClientInquiry:\n    def submit(self) -> None:\n        self.email = 'x'\n")
    result = tm.execute_spec_tdd_loop(_spec(), str(tmp_path))
    assert result["status"] == "FULFILLED"
    assert seen["module"] == "client_inquiry" and "email: str" in seen["source"]
    assert sorted(p.name for p in domain.iterdir() if p.suffix == ".py") == ["client_inquiry.py"]
    merged = (domain / "client_inquiry.py").read_text()
    assert "def submit" in merged and "email: str = ''" in merged
