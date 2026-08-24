"""
TDD State Machine — Hardened Red-Gate & 3-Strike Rollback Orchestrator.
Enforces programmatic test evaluation, OS test-file locking, pytest timeouts,
LibCST micro-context splicing, and automated dead-end git rollback handling.
"""

import os
import stat
import subprocess
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from onboarding.router_engine import BusinessSpec
from onboarding.cst_isolator import extract_class_cst, splice_class_cst


def evaluate_red_gate_result(
    exit_code: int,
    report_json: Optional[Dict[str, Any]] = None,
    stderr: str = ""
) -> Dict[str, Any]:
    """
    Evaluates Pytest execution in the RED phase.
    - Exit Code 0: Tautology error (REJECTED).
    - Exit Code 1 with AssertionError/Exception: Valid RED (APPROVED).
    - Exit Code 2 / SyntaxError / ImportError: Syntax error (REJECTED).
    """
    if exit_code == 0:
        return {
            "status": "REJECTED_TAUTOLOGY",
            "approved": False,
            "reason": "Test passed before logic was implemented (tautological false pass)."
        }

    # Inspect test crash reports and stderr for syntax or import errors
    crash_messages = []
    if report_json and "tests" in report_json:
        for t in report_json.get("tests", []):
            crash = t.get("call", {}).get("crash", {}).get("message", "")
            if crash:
                crash_messages.append(crash)

    all_error_text = (stderr + " " + " ".join(crash_messages)).lower()

    if exit_code == 2 or any(
        err in all_error_text
        for err in ["syntaxerror", "indentationerror", "importerror", "modulenotfounderror", "timed out"]
    ):
        return {
            "status": "REJECTED_SYNTAX_OR_EXEC",
            "approved": False,
            "reason": f"Test syntax, import, or timeout error: {stderr[:200]}"
        }

    if exit_code == 1:
        return {
            "status": "APPROVED_RED",
            "approved": True,
            "reason": "Test failed with AssertionError, TypeError (attribute expansion), or domain exception as expected in RED phase."
        }

    return {
        "status": "REJECTED_SYNTAX_OR_EXEC",
        "approved": False,
        "reason": f"Unexpected exit code {exit_code} in RED phase."
    }


def evaluate_green_gate_result(
    exit_code: int,
    report_json: Optional[Dict[str, Any]] = None,
    stderr: str = ""
) -> Dict[str, Any]:
    """Evaluates Pytest execution in the GREEN phase."""
    if exit_code == 0:
        return {
            "status": "APPROVED_GREEN",
            "approved": True,
            "reason": "All tests passed cleanly."
        }
    return {
        "status": "FAILED_GREEN",
        "approved": False,
        "reason": stderr or "Test assertions failed in GREEN phase."
    }


def lock_test_file(test_file_path: str) -> None:
    """Sets OS-level read-only permissions on test file during GREEN phase."""
    try:
        if os.path.exists(test_file_path):
            os.chmod(test_file_path, stat.S_IREAD)
    except Exception as e:
        print(f"Lock notice ({test_file_path}): {e}")


def unlock_test_file(test_file_path: str) -> None:
    """Restores read-write permissions on test file."""
    try:
        if os.path.exists(test_file_path):
            os.chmod(test_file_path, stat.S_IWRITE | stat.S_IREAD)
    except Exception as e:
        print(f"Unlock notice ({test_file_path}): {e}")


@dataclass
class TddExecutionState:
    spec: BusinessSpec
    phase: str = "INIT"  # "INIT" | "RED_GEN" | "RED_GATE" | "GREEN_GEN" | "GREEN_GATE" | "COMMITTED" | "DEAD_END"
    attempt: int = 0
    max_attempts: int = 3
    status: str = "PENDING"  # "PENDING" | "IN_PROGRESS" | "FULFILLED" | "REQUIRES_HUMAN_INTERVENTION"
    error_log: List[str] = field(default_factory=list)

    def advance_to_red(self):
        self.phase = "RED_GATE"
        self.status = "IN_PROGRESS"

    def advance_to_green(self):
        self.phase = "GREEN_GATE"
        self.attempt = 1

    def record_green_failure(self, error_message: str):
        self.error_log.append(error_message)
        self.attempt += 1
        if self.attempt > self.max_attempts:
            self.phase = "DEAD_END"
            self.status = "REQUIRES_HUMAN_INTERVENTION"

    def is_dead_end(self) -> bool:
        return self.attempt > self.max_attempts or self.phase == "DEAD_END"


def run_isolated_pytest(
    test_path: str,
    cwd: str,
    timeout_seconds: int = 5
) -> Dict[str, Any]:
    """
    Executes Pytest with pytest-json-report and hard timeout.
    Returns exit code, parsed report, and stdout/stderr.
    """
    report_file = os.path.join(cwd, ".pytest_report.json")
    if os.path.exists(report_file):
        try:
            os.remove(report_file)
        except Exception:
            pass

    cmd = [
        "python", "-m", "pytest",
        test_path,
        f"--timeout={timeout_seconds}",
        f"--json-report-file={report_file}",
        "--json-report"
    ]

    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout_seconds + 3
        )
        report_data = {}
        if os.path.exists(report_file):
            try:
                with open(report_file, "r", encoding="utf-8") as rf:
                    report_data = json.load(rf)
            except Exception:
                pass

        return {
            "exit_code": proc.returncode,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "report": report_data,
            "timed_out": False
        }
    except subprocess.TimeoutExpired:
        return {
            "exit_code": 2,
            "stdout": "",
            "stderr": f"Pytest execution timed out after {timeout_seconds} seconds.",
            "report": {},
            "timed_out": True
        }
