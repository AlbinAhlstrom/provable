"""
QA Rework Gate.

Company analogy: QA audits the build, files defects back to the responsible
department for rework (one retry, with the verdict as feedback), re-audits, and signs off with an honest verdict.
The auditor and the rework department are injected so the gate stays a pure
orchestration policy with no browser, LLM or filesystem dependency.
"""

from typing import Any, Callable, Dict, List

AuditFn = Callable[[], Dict[str, Any]]
ReworkFn = Callable[[List[str], List[str]], bool]

DEFAULT_MAX_REWORK_ATTEMPTS = 1  # one retry, fed the defects and console errors (retry policy)


def _has_defects(report: Dict[str, Any]) -> bool:
    if report.get("passed", True):
        return False
    return bool(report.get("defects") or report.get("console_errors"))


def _verdict(passed: bool, verdict: str, attempts: int, report: Dict[str, Any], **extra: Any) -> Dict[str, Any]:
    return {
        "passed": passed,
        "verdict": verdict,
        "attempts": attempts,
        "defects": list(report.get("defects") or []),
        "console_errors": list(report.get("console_errors") or []),
        **extra,
    }


def run_qa_gate(
    audit: AuditFn,
    rework: ReworkFn,
    max_rework_attempts: int = DEFAULT_MAX_REWORK_ATTEMPTS,
) -> Dict[str, Any]:
    """Audit, send defects to rework up to `max_rework_attempts` times, and report the final verdict."""
    try:
        report = audit()
    except Exception as err:
        return _verdict(False, "audit_error", 0, {}, error=str(err))

    attempts = 0
    while _has_defects(report):
        if attempts >= max_rework_attempts:
            return _verdict(False, "defects_remain", attempts, report)

        reworked = rework(
            list(report.get("defects") or []),
            list(report.get("console_errors") or []),
        )
        if not reworked:
            return _verdict(False, "rework_unavailable", attempts, report)
        attempts += 1

        try:
            report = audit()
        except Exception as err:
            return _verdict(False, "audit_error", attempts, {}, error=str(err))

    return _verdict(True, "passed", attempts, report)
