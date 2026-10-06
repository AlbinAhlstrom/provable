"""
TDD State Machine — Hardened Red-Gate & single-feedback-retry Orchestrator.
Enforces programmatic test evaluation, OS test-file locking, pytest timeouts,
LibCST micro-context splicing, and automated dead-end git rollback handling.
"""

from pipeline_trace import traced
import os
import sys
import re
import stat
import subprocess
import json
import hashlib
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from onboarding.router_engine import BusinessSpec
from onboarding.cst_isolator import (
    FragmentError, extract_class_cst, merge_module_fragment, module_import_lines, splice_class_cst
)


# Failures that mean the TEST is broken (not that the behavior is missing): never a valid RED.
_BROKEN_TEST_MARKERS = (
    "syntaxerror", "indentationerror", "importerror", "modulenotfounderror", "nameerror", "timed out",
    "fixture '", "module 'src.",
)


def _headline(text: str) -> str:
    """The most informative line of a failure text: the final 'E ' (error) line, else the first line."""
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    errors = [ln for ln in lines if ln.startswith("E ")]
    return (errors[-1][1:].strip() if errors else (lines[0] if lines else text))[:240]


def _failure_texts(report_json: Optional[Dict[str, Any]]) -> List[str]:
    """Crash messages of failed tests plus the text of collection errors, from a pytest-json-report."""
    texts: List[str] = []
    if not report_json:
        return texts
    for t in report_json.get("tests", []):
        crash = (t.get("call") or {}).get("crash", {}).get("message", "")
        if crash:
            texts.append(crash)
    for c in report_json.get("collectors", []):
        if c.get("outcome") == "failed" and c.get("longrepr"):
            texts.append(str(c["longrepr"]))
    return texts


@traced("tdd.red_gate")
def evaluate_red_gate_result(
    exit_code: int,
    report_json: Optional[Dict[str, Any]] = None,
    stderr: str = ""
) -> Dict[str, Any]:
    """
    Evaluates Pytest execution in the RED phase. A RED is only valid if the test fails because the
    BEHAVIOR is missing or wrong, never because the test itself is broken.
    - Exit Code 0: tautology (REJECTED).
    - Constructor misuse (TypeError in __init__), ImportError, NameError, SyntaxError, timeouts: broken test (REJECTED).
    - AssertionError, "DID NOT RAISE", missing attribute/method, method signature mismatch: valid RED (APPROVED).
    """
    if exit_code == 0:
        return {
            "status": "REJECTED_TAUTOLOGY",
            "approved": False,
            "reason": "Test passed before logic was implemented (tautological false pass)."
        }

    # A collection (import-time) error that runs through src/domain/ means the DOMAIN module is broken, not the test.
    for collector in (report_json or {}).get("collectors", []):
        text = str(collector.get("longrepr") or "")
        domain_files = re.findall(r"(src/domain/[\w/]+\.py)", text)
        if collector.get("outcome") == "failed" and domain_files:
            return {
                "status": "REJECTED_DOMAIN_BROKEN",
                "approved": False,
                "reason": f"The domain module does not import ({domain_files[-1]}): {_headline(text)}. This is not the test's fault."
            }

    messages = _failure_texts(report_json)
    for text in messages + ([stderr] if stderr else []):
        low = text.lower()
        if "typeerror" in low and "__init__" in low:
            return {
                "status": "REJECTED_BROKEN_TEST",
                "approved": False,
                "reason": f"Broken test, not a valid RED: the test constructs the class with arguments it does not accept ({_headline(text)}). Use only the fields listed in the class API."
            }
        if any(marker in low for marker in _BROKEN_TEST_MARKERS):
            return {
                "status": "REJECTED_SYNTAX_OR_EXEC",
                "approved": False,
                "reason": f"Broken test, not a valid RED: {_headline(text)}"
            }

    if exit_code == 1:
        return {
            "status": "APPROVED_RED",
            "approved": True,
            "reason": "Test fails because the specified behavior is missing or wrong (assertion, missing raise, missing method or signature mismatch)."
        }

    return {
        "status": "REJECTED_SYNTAX_OR_EXEC",
        "approved": False,
        "reason": f"Unexpected exit code {exit_code} in RED phase."
    }


@traced("tdd.green_gate")
def evaluate_green_gate_result(
    exit_code: int,
    report_json: Optional[Dict[str, Any]] = None,
    stderr: str = "",
    stdout: str = ""
) -> Dict[str, Any]:
    """Evaluates Pytest execution in the GREEN phase."""
    if exit_code == 0:
        return {
            "status": "APPROVED_GREEN",
            "approved": True,
            "reason": "All tests passed cleanly."
        }

    crash_messages = []
    if report_json and "tests" in report_json:
        for t in report_json.get("tests", []):
            crash = t.get("call", {}).get("crash", {}).get("message", "")
            if crash:
                crash_messages.append(crash)
            longrepr = t.get("call", {}).get("longrepr", "")
            if longrepr and isinstance(longrepr, str):
                crash_messages.append(longrepr)

    if report_json and "collectors" in report_json:
        for c in report_json.get("collectors", []):
            longrepr = c.get("longrepr", "")
            if longrepr and isinstance(longrepr, str):
                crash_messages.append(longrepr)

    detailed_reason = (stderr.strip() + " " + stdout.strip() + " " + " ".join(crash_messages)).strip() or f"Test assertions failed in GREEN phase (Exit code {exit_code})."
    return {
        "status": "FAILED_GREEN",
        "approved": False,
        "reason": detailed_reason
    }



import hashlib


class TestTamperingError(Exception):
    """Raised when test file content hash changes during the GREEN phase (anti-cheat violation)."""
    pass


def compute_test_file_hash(test_file_path: str) -> str:
    """Computes SHA-256 hash of the test file."""
    if not os.path.exists(test_file_path):
        return ""
    with open(test_file_path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def verify_test_file_integrity(test_file_path: str, expected_hash: str) -> bool:
    """Verifies that the test file has not been modified during the GREEN phase."""
    current_hash = compute_test_file_hash(test_file_path)
    if current_hash != expected_hash:
        raise TestTamperingError(
            f"Anti-Cheat Violation: Test file {test_file_path} was modified during GREEN phase! "
            f"Expected {expected_hash}, found {current_hash}"
        )
    return True


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
    max_attempts: int = 2  # first GREEN attempt + exactly one feedback retry
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


@traced("tdd.pytest")
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

    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{cwd}{os.pathsep}{current_pythonpath}"

    cmd = [
        sys.executable, "-m", "pytest",
        test_path,
        f"--timeout={timeout_seconds}",
        f"--json-report-file={report_file}",
        "--json-report"
    ]

    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            env=env,
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


def summarize_pytest_failure(result: Dict[str, Any], limit: int = 3000) -> str:
    """Concise, human-readable failure evidence from a run_isolated_pytest result (no raw JSON report)."""
    texts: List[str] = []
    report = result.get("report") or {}
    for t in report.get("tests", []):
        call = t.get("call") or {}
        if call.get("outcome") == "failed":
            texts.append(call.get("longrepr") or call.get("crash", {}).get("message", ""))
    for c in report.get("collectors", []):
        if c.get("outcome") == "failed" and c.get("longrepr"):
            texts.append(str(c["longrepr"]))
    text = "\n".join(t for t in texts if t) or (result.get("stderr") or result.get("stdout") or "")
    return text[-limit:]


def summarize_class_api(class_source: str, max_methods: int = 60) -> str:
    """Fields and method signatures of a class (no bodies), so prompts stay small however large the class grows."""
    import ast
    try:
        tree = ast.parse(class_source)
        cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    except (SyntaxError, StopIteration):
        return class_source[:2000]
    lines = [f"class {cls.name}:"]
    methods = 0
    for node in cls.body:
        if isinstance(node, ast.AnnAssign):
            lines.append(f"    {ast.unparse(node)}")
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            if methods < max_methods:
                ret = f" -> {ast.unparse(node.returns)}" if node.returns else ""
                lines.append(f"    def {node.name}({ast.unparse(node.args)}){ret}: ...")
            methods += 1
    return "\n".join(lines)


def lint_red_test(test_code: str, require_both_sides: bool = False) -> "tuple[bool, str]":
    """Cheap static checks on a generated RED test, run before pytest: it must be valid, behavioral and assert something.

    With require_both_sides (specs that state a numeric boundary) it must contain at least two cases: one beyond the
    boundary and one exactly at it, as separate test functions or a parametrized test.
    """
    import ast
    try:
        tree = ast.parse(test_code)
    except SyntaxError as e:
        return False, f"SyntaxError in the generated test: {e}"
    if not any(isinstance(n, ast.FunctionDef) and n.name.startswith("test_") for n in ast.walk(tree)):
        return False, "The module defines no test function (a function whose name starts with test_)."
    for n in ast.walk(tree):
        if isinstance(n, ast.Call):
            name = n.func.id if isinstance(n.func, ast.Name) else (n.func.value.id if isinstance(n.func, ast.Attribute) and isinstance(n.func.value, ast.Name) else "")
            if name in ("hasattr", "getattr", "inspect"):
                return False, f"The test uses {name}(): existence checks are not behavior tests. Exercise the scenario with concrete inputs and assert its outcome."
    has_assertion = any(isinstance(n, ast.Assert) for n in ast.walk(tree)) or "pytest.raises" in test_code
    if not has_assertion:
        return False, "The test asserts nothing (no assert statement and no pytest.raises)."
    if require_both_sides:
        test_functions = sum(1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_"))
        if test_functions < 2 and "parametrize" not in test_code:
            return False, (
                "The scenario states a boundary, so test BOTH sides of it: one case just beyond the boundary (rejected/invalid) "
                "and one exactly at the boundary (accepted/valid), as two test functions or one parametrized test."
            )
    return True, ""


def _quarantine_test(test_file_path: str, workspace_dir: str) -> str:
    """Moves an unverified test out of the regression suite (tests/unit) into tests/pending for a human to review."""
    import shutil
    pending_dir = os.path.join(workspace_dir, "tests", "pending")
    os.makedirs(pending_dir, exist_ok=True)
    target = os.path.join(pending_dir, os.path.basename(test_file_path))
    if os.path.exists(test_file_path):
        shutil.move(test_file_path, target)
    return target


def _failed_test_files(result: Dict[str, Any]) -> List[str]:
    """File names of the tests that failed in a pytest-json-report result."""
    names: List[str] = []
    for t in (result.get("report") or {}).get("tests", []):
        if t.get("outcome") == "failed" or (t.get("call") or {}).get("outcome") == "failed":
            name = os.path.basename(str(t.get("nodeid", "")).split("::")[0])
            if name and name not in names:
                names.append(name)
    for c in (result.get("report") or {}).get("collectors", []):
        if c.get("outcome") == "failed":
            names.append(os.path.basename(str(c.get("nodeid") or "collection")))
    return names


def collect_existing_tests(tests_dir: str, exclude: str, module_name: str, limit: int = 6000) -> str:
    """Source of the OTHER verified tests that exercise this module, so a new spec stays consistent with them.

    Without it each spec's test is written blind and specs end up contradicting one another (one test expects
    status "submitted" after submit(), the next expects "NEW"). Capped so the prompt cannot grow without bound.
    """
    if not os.path.isdir(tests_dir):
        return ""
    needle = f"src.domain.{module_name}"
    chunks: List[str] = []
    for name in sorted(os.listdir(tests_dir)):
        path = os.path.join(tests_dir, name)
        if not name.startswith("test_spec_") or not name.endswith(".py"):
            continue
        if exclude and os.path.abspath(path) == os.path.abspath(exclude):
            continue
        with open(path, "r", encoding="utf-8") as f:
            source = f.read()
        if needle in source:
            chunks.append(f"# {name}\n{source.strip()}\n")
    return "\n".join(chunks)[:limit]


@traced("tdd.red_generate")
def generate_red_test(
    spec: BusinessSpec,
    class_source: str,
    module_name: str,
    class_name: str,
    rejection_feedback: str = "",
    existing_tests: str = ""
) -> str:
    """Asks the LLM for a behavioral pytest module that encodes the spec's Given/When/Then.

    The prompt shows the class's real constructor/method API so the test cannot invent arguments, and
    on the single retry it carries the gate's or linter's rejection reason.
    """
    import agent_orchestrator

    feedback_block = (
        f"\n## Your previous test was REJECTED. Fix exactly this problem:\n{rejection_feedback}\n"
        if rejection_feedback else ""
    )
    prompt = agent_orchestrator.load_prompt("red_test_generation.md", {
        "spec_title": spec.title,
        "spec_description": spec.description,
        "spec_given_when_then": spec.given_when_then,
        "module_name": module_name,
        "target_class_name": class_name,
        "class_api": summarize_class_api(class_source),
        "existing_tests": existing_tests or "(none yet: this is the first verified test for this class)",
        "feedback_block": feedback_block,
    })
    raw = agent_orchestrator.call_gemini(prompt, stage="red_test_generation")
    if not raw or not raw.strip():
        reason = agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response"
        raise RuntimeError(f"RED test generation failed: {reason}")
    match = re.search(r"```(?:python)?\s*\n(.*?)```", raw, re.DOTALL)
    return (match.group(1) if match else raw).strip() + "\n"


@traced("tdd.green_synthesize")
def synthesize_green_class_implementation(
    extracted_class: str,
    target_class_name: str,
    spec: BusinessSpec,
    failure_output: str = "",
    test_source: str = "",
    module_imports: str = "",
    existing_tests: str = ""
) -> str:
    """Synthesizes the GREEN phase domain class implementation using LLM micro-context prompt.

    Extracts the target class via LibCST, provides the frozen RED test and its failure, and prompts the
    model to return the corrected Python class definition.

    Args:
        extracted_class: The existing Python code of the target class extracted via LibCST.
        target_class_name: The name of the class to mutate and repair.
        spec: The BusinessSpec containing BDD scenario and mutation requirements.
        failure_output: Concise evidence of why the frozen test currently fails.
        test_source: The frozen RED test the implementation must satisfy.
        module_imports: The import lines the target module already has.

    Returns:
        A module fragment (imports + helper classes + the target class) for merge_module_fragment.

    Raises:
        RuntimeError: If the LLM returns nothing usable. There is deliberately NO fallback stub: a fake
            implementation would let a provider outage produce FULFILLED specs.
    """
    import agent_orchestrator

    prompt = agent_orchestrator.load_prompt("green_class_repair.md", {
        "extracted_class_code": extracted_class,
        "spec_title": spec.title,
        "spec_given_when_then": spec.given_when_then,
        "target_aggregate": spec.target_aggregate or target_class_name,
        "spec_type": spec.spec_type,
        "test_source": test_source or "(no test source available)",
        "module_imports": module_imports or "(none)",
        "existing_tests": existing_tests or "(none yet)",
        "failure_output": failure_output or "The frozen test does not pass yet.",
        "target_class_name": target_class_name
    })

    raw_response = agent_orchestrator.call_gemini(prompt, stage="green_code_repair")
    if raw_response and raw_response.strip():


        # Match python code block if present
        code_block_match = re.search(r"```(?:python)?\s*(.*?)\s*```", raw_response, re.DOTALL)
        candidate = code_block_match.group(1).strip() if code_block_match else raw_response.strip()

        # If candidate has conversational text before @dataclass or class, trim it
        if f"class {target_class_name}" in candidate:
            class_idx = candidate.find(f"class {target_class_name}")
            prefix = candidate[:class_idx]
            dataclass_idx = prefix.rfind("@dataclass")
            if dataclass_idx != -1:
                candidate = candidate[dataclass_idx:].strip()
            else:
                candidate = candidate[class_idx:].strip()

            try:
                import ast
                ast.parse(candidate)
                return candidate + "\n"
            except Exception as syn_err:
                print(f"Synthesized class syntax error notice: {syn_err}")


    reason = agent_orchestrator.LAST_LLM_ERROR or f"the response did not contain a definition of class {target_class_name}"
    raise RuntimeError(f"GREEN synthesis failed: {reason}")


@traced("tdd.run_loop")
def execute_spec_tdd_loop(spec: BusinessSpec, workspace_dir: str) -> Dict[str, Any]:
    """
    Synchronous flat TDD loop execution:
    RED -> GREEN (with LibCST micro-context extraction) -> Hash Lock Anti-Cheat -> COMMIT.
    """
    state = TddExecutionState(spec=spec)
    state.advance_to_red()

    target_class = spec.target_aggregate or "Pallet"
    from onboarding.skeleton_builder import to_snake_case
    target_mod_name = to_snake_case(target_class)  # same module name the skeleton/routers/repositories import
    
    domain_dir = os.path.join(workspace_dir, "src", "domain")
    tests_dir = os.path.join(workspace_dir, "tests", "unit")
    os.makedirs(domain_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    # Locate canonical domain file
    domain_file = None
    if os.path.exists(domain_dir):
        # 1. Canonical snake_case module match (e.g. maintenance_work_order.py)
        candidate_canonical = os.path.join(domain_dir, f"{target_mod_name}.py")
        if os.path.exists(candidate_canonical):
            domain_file = candidate_canonical
        else:
            # 2. Lowercase direct match fallback
            candidate_lower = os.path.join(domain_dir, f"{target_class.lower()}.py")
            if os.path.exists(candidate_lower):
                domain_file = candidate_lower
            else:
                # 3. Search all entity domain files for target_class definition
                for fname in os.listdir(domain_dir):
                    if fname.endswith(".py") and not fname.startswith("__") and fname not in ["events.py", "exceptions.py"]:
                        fpath = os.path.join(domain_dir, fname)
                        try:
                            with open(fpath, "r", encoding="utf-8") as f:
                                content = f.read()
                                if re.search(rf"\bclass\s+{re.escape(target_class)}\b", content):
                                    domain_file = fpath
                                    break
                        except Exception:
                            pass

    if not domain_file or not os.path.exists(domain_file):
        domain_file = os.path.join(domain_dir, f"{target_mod_name}.py")
        init_code = f'''import math
from dataclasses import dataclass, field
from datetime import datetime, date, timezone, timedelta
from typing import List, Optional, Dict, Any, Union, Set, Tuple, Callable

try:
    from src.domain.exceptions import DomainError, StaleDataError, InvariantViolation, MaintenanceRequiredError, MaintenanceLockoutError, ReservationConflictError, BusinessRuleViolation
    from src.domain.events import DomainEvent, MaintenanceRequiredEvent, MaintenanceLockedEvent
except ImportError:
    try:
        from domain.exceptions import DomainError, StaleDataError, InvariantViolation, MaintenanceRequiredError, MaintenanceLockoutError, ReservationConflictError, BusinessRuleViolation
        from domain.events import DomainEvent, MaintenanceRequiredEvent, MaintenanceLockedEvent
    except ImportError:
        pass

@dataclass
class {target_class}:
    id: str
    name: str = "Standard {target_class}"
    events: List[Any] = field(default_factory=list)
'''
        with open(domain_file, "w", encoding="utf-8") as f:
            f.write(init_code)

    used_module = os.path.splitext(os.path.basename(domain_file))[0]

    # -------------------------------------------------------------
    # 1. RED Phase: the LLM writes a behavioral test from the BDD spec; the gate checks it fails for the RIGHT reason
    # -------------------------------------------------------------
    spec_clean_id = spec.spec_id.lower().replace("-", "_")
    test_file_path = os.path.join(tests_dir, f"test_{spec_clean_id}.py")
    scenario = spec.given_when_then or ""
    with open(domain_file, "r", encoding="utf-8") as f:
        initial_domain_source = f.read()
    extracted_class_for_red = extract_class_cst(initial_domain_source, target_class) or f"@dataclass\nclass {target_class}:\n    id: str\n"

    with open(domain_file, "r", encoding="utf-8") as f:
        current_source = f.read()
    current_class = extract_class_cst(current_source, target_class) or f"@dataclass\nclass {target_class}:\n    id: str\n"

    # Retry policy (rule 03 section 4): at most ONE regeneration, only because the lint or the RED gate rejected
    # the first test, and the rejection reason is fed back to the test generator.
    existing_tests = collect_existing_tests(tests_dir, exclude=test_file_path, module_name=used_module)
    red_feedback = ""
    red_result: Dict[str, Any] = {}
    red_eval: Dict[str, Any] = {}
    red_attempts: List[Dict[str, Any]] = []
    domain_broken = False
    test_code = ""
    for red_attempt in (1, 2):
        test_code = generate_red_test(spec, current_class, used_module, target_class,
                                      rejection_feedback=red_feedback, existing_tests=existing_tests)
        lint_ok, lint_reason = lint_red_test(test_code, require_both_sides=bool(spec.is_mathematical_boundary))
        if not lint_ok:
            red_attempts.append({"attempt": red_attempt, "approved": False, "reason": lint_reason})
            red_feedback = lint_reason
            continue

        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_code)
        # 5-line Hash Lock: snapshot the approved test file's hash before the GREEN phase
        initial_test_hash = compute_test_file_hash(test_file_path)
        red_result = run_isolated_pytest(test_file_path, cwd=workspace_dir)
        red_eval = evaluate_red_gate_result(red_result["exit_code"], red_result.get("report"), red_result.get("stderr"))
        red_attempts.append({"attempt": red_attempt, "approved": red_eval["approved"], "reason": red_eval.get("reason")})
        if red_eval["approved"]:
            break
        if red_eval.get("status") == "REJECTED_DOMAIN_BROKEN":
            # Regenerating the test cannot help: the domain module itself does not import. Fail loudly now.
            domain_broken = True
            break
        red_feedback = f"{red_eval.get('reason')}\n{summarize_pytest_failure(red_result)}"
    else:
        state.phase = "DEAD_END"
        state.status = "REQUIRES_HUMAN_INTERVENTION"
        if os.path.exists(test_file_path):  # a test rejected twice is known to be broken: do not keep it
            os.remove(test_file_path)
        return {
            "success": False,
            "status": state.status,
            "phase": "RED_GATE",
            "spec_id": spec.spec_id,
            "error": red_attempts[-1]["reason"],
            "red_attempts": red_attempts,
            "test_source": test_code
        }

    if domain_broken:
        state.phase = "DEAD_END"
        state.status = "REQUIRES_HUMAN_INTERVENTION"
        # The test itself was never judged, so keep it for a human instead of letting it fail the regression suite.
        return {
            "success": False,
            "status": state.status,
            "phase": "RED_GATE",
            "spec_id": spec.spec_id,
            "error": red_attempts[-1]["reason"],
            "red_attempts": red_attempts,
            "test_source": test_code,
            "pending_test": _quarantine_test(test_file_path, workspace_dir)
        }

    state.advance_to_green()

    failure_msg = summarize_pytest_failure(red_result)
    default_class = f'''@dataclass
class {target_class}:
    id: str
    name: str = "Standard {target_class}"
'''
    attempts: List[Dict[str, Any]] = []
    domain_before = open(domain_file, "r", encoding="utf-8").read()

    def rollback() -> None:
        """A spec that does not reach GREEN must leave the domain exactly as it found it."""
        with open(domain_file, "w", encoding="utf-8") as f:
            f.write(domain_before)

    # Retry policy (rule 03 section 4): at most ONE retry, and only because the GREEN gate (or the merge of the
    # model's answer) rejected the first attempt; the verdict and the failing test output are fed back to the
    # generator. Provider errors, tampering and anything else fail loudly without a retry.
    try:
        while True:
            with open(domain_file, "r", encoding="utf-8") as f:
                domain_source = f.read()
            extracted_class = extract_class_cst(domain_source, target_class) or default_class

            # LLM-driven micro-context synthesis: a module fragment (imports + helper classes + the class)
            fragment = synthesize_green_class_implementation(
                extracted_class=extracted_class,
                target_class_name=target_class,
                spec=spec,
                failure_output=failure_msg,
                test_source=test_code,
                module_imports=module_import_lines(domain_source),
                existing_tests=existing_tests
            )

            try:
                new_domain_source = merge_module_fragment(domain_source, target_class, fragment)
            except FragmentError as err:
                green_result = {"exit_code": 1, "stderr": str(err), "report": None}
                green_eval = {"status": "REJECTED_UNMERGEABLE", "approved": False, "reason": str(err)}
            else:
                with open(domain_file, "w", encoding="utf-8") as f:
                    f.write(new_domain_source)

                # Verify anti-cheat test file integrity hash
                verify_test_file_integrity(test_file_path, initial_test_hash)

                # Run GREEN phase test execution
                green_result = run_isolated_pytest(test_file_path, cwd=workspace_dir)
                green_eval = evaluate_green_gate_result(green_result["exit_code"], green_result.get("report"), green_result.get("stderr"))

                # Regression gate: the new implementation must not break any earlier, verified spec.
                if green_eval["approved"]:
                    regression = run_isolated_pytest(tests_dir, cwd=workspace_dir, timeout_seconds=30)
                    if regression["exit_code"] != 0:
                        broken = _failed_test_files(regression) or ["(unknown)"]
                        green_result = regression
                        green_eval = {
                            "status": "REJECTED_REGRESSION",
                            "approved": False,
                            "reason": f"Regression: your change makes earlier tests fail again: {', '.join(broken)}. Keep every existing behavior."
                        }
            attempts.append({"attempt": state.attempt, "approved": green_eval["approved"], "reason": green_eval.get("reason")})

            if green_eval["approved"]:
                state.phase = "COMMITTED"
                state.status = "FULFILLED"
                return {
                    "success": True,
                    "status": "FULFILLED",
                    "phase": "COMMITTED",
                    "spec_id": spec.spec_id,
                    "test_file": test_file_path,
                    "red_eval": red_eval,
                    "green_eval": green_eval,
                    "red_attempts": red_attempts,
                    "test_source": test_code,
                    "attempts": attempts
                }

            state.record_green_failure(green_eval.get("reason", "Test failed in green phase"))
            if state.is_dead_end():
                rollback()
                pending = _quarantine_test(test_file_path, workspace_dir)
                return {
                    "success": False,
                    "status": state.status,
                    "phase": state.phase,
                    "spec_id": spec.spec_id,
                    "error": green_eval.get("reason"),
                    "red_attempts": red_attempts,
                    "test_source": test_code,
                    "attempts": attempts,
                    "error_log": list(state.error_log),
                    "rolled_back": True,
                    "pending_test": pending
                }

            failure_msg = (
                f"The previous GREEN attempt was rejected: {green_eval.get('reason')}\n"
                + summarize_pytest_failure(green_result)
            )
    except BaseException:
        rollback()
        _quarantine_test(test_file_path, workspace_dir)
        raise
