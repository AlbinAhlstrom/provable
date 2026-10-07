"""
Unit tests for the QA rework gate.

The gate models a company QA department: it audits, files defects back to the
responsible department for rework (bounded), and reports an honest final verdict.
"""

from onboarding.qa_gate import run_qa_gate

CLEAN = {"passed": True, "defects": [], "console_errors": []}
BROKEN = {"passed": False, "defects": ["overflow at 375px"], "console_errors": []}


def _audit_sequence(*reports):
    calls = {"n": 0}

    def audit():
        i = min(calls["n"], len(reports) - 1)
        calls["n"] += 1
        return reports[i]

    audit.calls = calls
    return audit


def test_clean_audit_passes_without_rework():
    heal_calls = []
    verdict = run_qa_gate(_audit_sequence(CLEAN), lambda d, c: heal_calls.append(d) or True)

    assert verdict["passed"] is True
    assert verdict["attempts"] == 0
    assert heal_calls == []


def test_defect_is_reworked_then_passes_on_recheck():
    audit = _audit_sequence(BROKEN, CLEAN)
    verdict = run_qa_gate(audit, lambda defects, errors: True)

    assert verdict["passed"] is True
    assert verdict["attempts"] == 1
    assert audit.calls["n"] == 2


def test_persistent_defect_fails_after_bounded_attempts():
    audit = _audit_sequence(BROKEN)  # always broken
    heal_calls = []
    verdict = run_qa_gate(
        audit, lambda d, c: heal_calls.append(d) or True, max_rework_attempts=2
    )

    assert verdict["passed"] is False
    assert verdict["attempts"] == 2
    assert len(heal_calls) == 2
    assert verdict["defects"] == ["overflow at 375px"]


def test_skipped_rework_fails_without_retry():
    audit = _audit_sequence(BROKEN)
    verdict = run_qa_gate(audit, lambda d, c: False)

    assert verdict["passed"] is False
    assert verdict["verdict"] == "rework_unavailable"
    assert audit.calls["n"] == 1


def test_audit_crash_is_not_reported_as_pass():
    def audit():
        raise RuntimeError("browser unavailable")

    verdict = run_qa_gate(audit, lambda d, c: True)

    assert verdict["passed"] is False
    assert verdict["verdict"] == "audit_error"
    assert "browser unavailable" in verdict["error"]


def test_console_errors_alone_trigger_rework():
    noisy = {"passed": False, "defects": [], "console_errors": ["TypeError: x"]}
    seen = {}

    def heal(defects, errors):
        seen["errors"] = errors
        return True

    verdict = run_qa_gate(_audit_sequence(noisy, CLEAN), heal)

    assert verdict["passed"] is True
    assert seen["errors"] == ["TypeError: x"]


def test_default_policy_is_exactly_one_rework_with_feedback():
    """Retry policy: one retry, fed the verdict (defects and console errors), then fail loudly."""
    audit = _audit_sequence({"passed": False, "defects": ["blank root"], "console_errors": ["boom"]})
    seen = []
    verdict = run_qa_gate(audit, lambda defects, errors: seen.append((defects, errors)) or True)

    assert verdict["passed"] is False
    assert verdict["verdict"] == "defects_remain"
    assert verdict["attempts"] == 1
    assert seen == [(["blank root"], ["boom"])]
