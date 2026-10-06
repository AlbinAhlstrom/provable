import pytest
import os
import stat
from onboarding.router_engine import BusinessSpec
from service_layer.tdd_machine import (
    evaluate_red_gate_result,
    evaluate_green_gate_result,
    lock_test_file,
    unlock_test_file,
    TddExecutionState
)

def test_evaluate_red_gate_rejects_tautology_exit_code_zero():
    # If a test passes before code is implemented, it is a tautological test error
    result = evaluate_red_gate_result(exit_code=0, report_json={"summary": {"passed": 1, "total": 1}})
    assert result["status"] == "REJECTED_TAUTOLOGY"
    assert result["approved"] is False

def test_evaluate_red_gate_approves_exit_code_one_with_assertion_error():
    report = {
        "summary": {"failed": 1, "total": 1},
        "tests": [
            {
                "nodeid": "tests/test_spec_001.py::test_rule",
                "outcome": "failed",
                "call": {"crash": {"message": "AssertionError: Expected 20.0, got 0.0"}}
            }
        ]
    }
    result = evaluate_red_gate_result(exit_code=1, report_json=report)
    assert result["status"] == "APPROVED_RED"
    assert result["approved"] is True

def test_evaluate_red_gate_rejects_syntax_or_import_error():
    report = {
        "summary": {"failed": 1, "total": 1},
        "tests": [
            {
                "nodeid": "tests/test_spec_001.py",
                "outcome": "failed",
                "call": {"crash": {"message": "SyntaxError: invalid syntax"}}
            }
        ]
    }
    result = evaluate_red_gate_result(exit_code=2, report_json=report, stderr="SyntaxError: invalid syntax")
    assert result["status"] == "REJECTED_SYNTAX_OR_EXEC"
    assert result["approved"] is False

def test_test_file_locking_and_unlocking(tmp_path):
    test_file = tmp_path / "test_spec_001.py"
    test_file.write_text("def test_dummy(): assert True")
    
    # Lock file
    lock_test_file(str(test_file))
    
    # Assert file is read-only
    file_mode = os.stat(str(test_file)).st_mode
    assert not (file_mode & stat.S_IWUSR)
    
    # Unlock file
    unlock_test_file(str(test_file))
    file_mode_unlocked = os.stat(str(test_file)).st_mode
    assert bool(file_mode_unlocked & stat.S_IWUSR)

def test_tdd_state_machine_transitions():
    spec = BusinessSpec(
        spec_id="SPEC-001",
        title="Enforce Pizza Minimum Order",
        description="Orders below $15 are rejected.",
        given_when_then="Given order under $15 When validating Then raises MinimumOrderViolation",
        target_aggregate="PizzaOrder",
        is_mathematical_boundary=True
    )
    state = TddExecutionState(spec=spec)
    assert state.phase == "INIT"
    assert state.attempt == 0
    assert state.status == "PENDING"
    
    state.advance_to_red()
    assert state.phase == "RED_GATE"
    
    state.advance_to_green()
    assert state.phase == "GREEN_GATE"
    
    # Retry policy: first failure still allows exactly one feedback retry; the second is a dead end.
    state.record_green_failure("AssertionError in green")
    assert state.is_dead_end() is False
    state.record_green_failure("AssertionError in green")

    assert state.is_dead_end() is True
    assert state.status == "REQUIRES_HUMAN_INTERVENTION"


def test_synthesize_green_class_implementation_with_llm(monkeypatch):
    from service_layer.tdd_machine import synthesize_green_class_implementation
    import agent_orchestrator

    mock_llm_response = '''```python
@dataclass
class Pallet:
    id: str
    weight: float = 0.0
    
    def validate_invariants(self) -> bool:
        """Validates that pallet weight does not exceed capacity."""
        return self.weight <= 1000.0
```'''
    monkeypatch.setattr(agent_orchestrator, "call_gemini", lambda prompt, stage: mock_llm_response)

    spec = BusinessSpec(
        spec_id="SPEC-002",
        title="Enforce Pallet Weight Limit",
        description="Pallet weight cannot exceed 1000kg.",
        given_when_then="Given a pallet When weight is 1000 Then validation succeeds",
        target_aggregate="Pallet",
        spec_type="DOMAIN_INVARIANT"
    )

    initial_class = """@dataclass
class Pallet:
    id: str
"""

    result = synthesize_green_class_implementation(
        extracted_class=initial_class,
        target_class_name="Pallet",
        spec=spec,
        failure_output="AssertionError: Pallet has no attribute validate_invariants"
    )

    assert "def validate_invariants" in result
    assert "class Pallet" in result
    assert "```" not in result

