"""
TDD State Machine — Hardened Red-Gate & single-feedback-retry Orchestrator.
Enforces programmatic test evaluation, OS test-file locking, pytest timeouts,
LibCST micro-context splicing, and automated dead-end git rollback handling.
"""

from pipeline_trace import traced
from service_layer.hollow_check import fails_without_behaviour
import os
import sys
import uuid
import re
import stat
import subprocess
import json
import hashlib
from typing import Dict, Any, List, Optional
from onboarding.action_protocol import format_interface_contract
from dataclasses import dataclass, field
from onboarding.router_engine import BusinessSpec
from onboarding.cst_isolator import (
    FragmentError, extract_class_cst, merge_module_fragment, module_helpers_source, module_import_lines, splice_class_cst
)


# Failures that mean the TEST is broken (not that the behavior is missing): never a valid RED.
_BROKEN_TEST_MARKERS = ("timed out", "fixture '", "module 'src.")
# Read as whole names: a product's own refusal may end in one of them (`EmptyNameError`, expected by a valid test).
_BROKEN_TEST_ERRORS = re.compile(
    r"(?<![a-z])(?:syntaxerror|indentationerror|importerror|modulenotfounderror|nameerror)(?![a-z])")


GIVEN_FAILED = "AssertionError: Given:"  # how a failed check of a test's own arrangement reads (red_test_generation.md)
REGRESSION_TIMEOUT_S = 30  # the domain tests in tests/unit; the page's browser checks live in tests/acceptance


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
    - An assertion whose message begins "Given:": the test's arrangement is not the one it states (REJECTED). The
      writer asserts the facts its expectation rests on before it acts, so a state typed otherwise than planned is
      caught here, by this run, and not by whoever implements against it.
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
    for text in messages:
        if GIVEN_FAILED in text:
            fact = text.split(GIVEN_FAILED, 1)[1].splitlines()[0].strip()
            return {
                "status": "REJECTED_GIVEN",
                "approved": False,
                "reason": f"The test does not arrange the state it says it does, so what it expects rests on a state "
                          f"it never built. This did not hold after the arrangement: \"{fact}\". Correct the "
                          f"arrangement so that it does."
            }
    for text in messages + ([stderr] if stderr else []):
        low = text.lower()
        if "typeerror" in low and "__init__" in low:
            return {
                "status": "REJECTED_BROKEN_TEST",
                "approved": False,
                "reason": f"Broken test, not a valid RED: the test constructs the class with arguments it does not accept ({_headline(text)}). Use only the fields listed in the class API."
            }
        if any(marker in low for marker in _BROKEN_TEST_MARKERS) or _BROKEN_TEST_ERRORS.search(low):
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

    said = [ln.strip() for ln in stderr.splitlines() if "error:" in ln.lower()]  # e.g. pytest's usage error
    why = f": {said[-1][:240]}" if said else ""
    return {
        "status": "REJECTED_SYNTAX_OR_EXEC",
        "approved": False,
        "reason": f"Unexpected exit code {exit_code} in RED phase{why}."
    }


@traced("tdd.green_gate")
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
    timeout_seconds: int = 5,
    extra_env: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Executes Pytest with pytest-json-report and hard timeout.
    Returns exit code, parsed report, and stdout/stderr. `extra_env` is added to the run's environment.
    """
    # One report file per run: specs' tests are run side by side (service_layer/tdd_batch.py)
    report_file = os.path.join(cwd, f".pytest_report_{uuid.uuid4().hex}.json")

    env = os.environ.copy()
    current_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{cwd}{os.pathsep}{current_pythonpath}"
    env.update(extra_env or {})

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
            os.remove(report_file)

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
    described = ast.get_docstring(cls)
    if described:  # what the class says about itself, e.g. what one item of a list of its parts holds
        lines.append('    """' + described.replace("\n", "\n    ") + '"""')
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


# A reconsidered test is traced through the implementation, which the default (low) effort gets wrong about as
# often as the first draft did; at medium effort an answer takes up to a minute, so it is kept for this one call
LIMIT_NOTE = ("\n- **States a limit**: yes. Rule 7 below applies to this scenario: at least two cases, one just beyond "
              "the limit and one exactly at it.")
CAREFUL_EFFORT = "medium"
CAREFUL_TIMEOUT_S = 180.0
# Seconds a first draft may take. The one test of a whole class of actions is among the largest answers of a build:
# 31 s for eight actions on a quick day, cut off at the 60 s of an ordinary call on a slow one.
RED_TIMEOUT_S = 180.0
# Seconds the code of a class may take. One answer holds every action of the class: 13,000 tokens took 55 s in one
# build, and the retry with the failures, which is longer still, was cut off at the 60 s of an ordinary call.
GREEN_TIMEOUT_S = 180.0


@traced("tdd.red_generate")
def generate_red_test(
    spec: BusinessSpec,
    class_source: str,
    module_name: str,
    class_name: str,
    rejection_feedback: str = "",
    existing_tests: str = "",
    interface_contract: str = "",
    careful: bool = False,
    other_rules: str = "",
) -> str:
    """Asks the LLM for a behavioral pytest module that encodes the spec's Given/When/Then.

    The prompt shows the class's real constructor/method API so the test cannot invent arguments, and
    on the single retry it carries the gate's or linter's rejection reason. `careful` is for a test that has
    to be traced through an implementation (a reconsidered test): the writer thinks longer and is given the time.
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
        "interface_contract": interface_contract or "(none: no interface method has been promised for this class)",
        "feedback_block": feedback_block,
        "limit_note": LIMIT_NOTE if spec.is_mathematical_boundary else "",
        "situation_block": f"\n- **Situation** {spec.situation}" if spec.situation else "",
        "other_rules": other_rules or "(none: this is the only rule being written for this class)",
    })
    thought = dict(reasoning_effort=CAREFUL_EFFORT, timeout_s=CAREFUL_TIMEOUT_S) if careful else dict(timeout_s=RED_TIMEOUT_S)
    raw = agent_orchestrator.call_gemini(prompt, stage="red_test_generation", **thought)
    if not raw or not raw.strip():
        reason = agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response"
        raise RuntimeError(f"RED test generation failed: {reason}")
    return _code_of(raw)


def _code_of(answer: str) -> str:
    """The code of an answer: what its fenced blocks hold, in the order given, whatever words stand around
    them; otherwise the answer itself. A writer that hands over a class's helpers in one block and the class in
    the next has answered with all of it."""
    blocks = re.findall(r"```(?:python)?\s*\n(.*?)```", answer, re.DOTALL)
    return "\n\n\n".join(block.strip() for block in blocks or [answer]) + "\n"


@traced("tdd.green_synthesize")
def synthesize_green_class_implementation(
    extracted_class: str,
    target_class_name: str,
    spec: BusinessSpec,
    failure_output: str = "",
    test_source: str = "",
    module_imports: str = "",
    existing_tests: str = "",
    module_helpers: str = ""
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
        "module_helpers": module_helpers or "(none)",
        "existing_tests": existing_tests or "(none yet)",
        "failure_output": failure_output or "The frozen test does not pass yet.",
        "target_class_name": target_class_name
    })

    raw_response = agent_orchestrator.call_gemini(prompt, stage="green_code_repair", timeout_s=GREEN_TIMEOUT_S)

    if raw_response and raw_response.strip():
        clean_code = _code_of(raw_response)
        if f"class {target_class_name}" in clean_code:
            return clean_code

    if raw_response and raw_response.strip():
        raise NoClassInAnswer(target_class_name, raw_response)
    raise RuntimeError(f"GREEN synthesis failed: {agent_orchestrator.LAST_LLM_ERROR or 'the response was empty'}")


class NoClassInAnswer(RuntimeError):
    """The code writer answered, and the answer holds no definition of the class: it wrote words in place of code
    (typically that the frozen test expects the wrong thing). No provider error, and no code either."""

    def __init__(self, class_name: str, answer: str):
        super().__init__(f"GREEN synthesis failed: the response did not contain a definition of class {class_name}")
        self.answer = answer


@dataclass
class DomainTarget:
    """Where a spec's class lives in the workspace."""
    class_name: str
    module_name: str   # the module the tests import it from (src.domain.<module_name>)
    domain_file: str
    tests_dir: str


def locate_domain_target(spec: BusinessSpec, workspace_dir: str) -> DomainTarget:
    """The class a spec is about and its module, created as a bare dataclass when the workspace has none."""
    target_class = spec.target_aggregate or "Pallet"
    from onboarding.skeleton_builder import to_snake_case
    target_mod_name = to_snake_case(target_class)  # same module name the skeleton/routers/repositories import

    domain_dir = os.path.join(workspace_dir, "src", "domain")
    tests_dir = os.path.join(workspace_dir, "tests", "unit")
    os.makedirs(domain_dir, exist_ok=True)
    os.makedirs(tests_dir, exist_ok=True)

    domain_file = os.path.join(domain_dir, f"{target_mod_name}.py")
    if not os.path.exists(domain_file):
        model_file = os.path.join(domain_dir, "model.py")
        if os.path.exists(model_file) and target_class in open(model_file, encoding="utf-8").read():
            domain_file = model_file
        else:
            init_code = f'''from dataclasses import dataclass, field
from typing import List, Optional

class DomainError(Exception):
    pass

@dataclass
class {target_class}:
    id: str
    name: str = "Standard {target_class}"
'''
            with open(domain_file, "w", encoding="utf-8") as f:
                f.write(init_code)

    used_module = target_mod_name if domain_file.endswith(f"{target_mod_name}.py") else "model"
    return DomainTarget(class_name=target_class, module_name=used_module, domain_file=domain_file, tests_dir=tests_dir)


def spec_test_path(spec: BusinessSpec, tests_dir: str) -> str:
    return os.path.join(tests_dir, f"test_{spec.spec_id.lower().replace('-', '_')}.py")


@dataclass
class RedOutcome:
    """What the RED phase delivered for one spec. `verdict` is one of
    approved (a valid failing test, locked by `test_hash`) | already_satisfied (the class enforces the rule; the test
    is kept as its guard) | rejected (two tests were refused; none is kept) | domain_broken (the domain module does
    not import; the test was never judged)."""
    verdict: str
    test_file_path: str
    test_code: str = ""
    test_hash: str = ""
    result: Dict[str, Any] = field(default_factory=dict)      # the pytest run of the approved test
    evaluation: Dict[str, Any] = field(default_factory=dict)  # the RED gate's verdict
    attempts: List[Dict[str, Any]] = field(default_factory=list)


def _sent_back(reason: str, test_code: str) -> str:
    """What the test writer is told on its one regeneration: the verdict, and the test it was given on. Without the
    test it writes a new one from nothing and loses what the first had right (the cases on both sides of a limit)."""
    return (f"{reason}\n\nThe test that was refused (keep everything in it the reason above does not name):\n"
            f"```python\n{test_code.strip()}\n```")


def run_red_phase(spec: BusinessSpec, target: DomainTarget, workspace_dir: str, existing_tests: str,
                  action_manifest: Optional[Dict[str, Any]] = None, other_rules: str = "",
                  first_test: Optional[str] = None) -> RedOutcome:
    """The LLM writes a behavioural test from the BDD spec; the gate checks it fails for the RIGHT reason.

    Retry policy (.claude/rules/pipeline.md): at most ONE regeneration, only because the lint or the RED gate rejected
    the first test, and the rejection reason is fed back to the test generator.

    `first_test` is the spec's first test when it is already written (a kickstart writes the first tests of a class
    in one answer, `onboarding/first_tests.py`): it is judged as the first attempt, and only the regeneration is a
    call of this spec's own. An empty one (the answer held no test for this spec) is refused like any other."""
    test_file_path = spec_test_path(spec, target.tests_dir)
    with open(target.domain_file, "r", encoding="utf-8") as f:
        current_source = f.read()
    current_class = extract_class_cst(current_source, target.class_name) or f"@dataclass\nclass {target.class_name}:\n    id: str\n"

    red_feedback = ""
    red_result: Dict[str, Any] = {}
    red_eval: Dict[str, Any] = {}
    red_attempts: List[Dict[str, Any]] = []
    test_code = ""
    for red_attempt in (1, 2):
        test_code = first_test if red_attempt == 1 and first_test is not None else generate_red_test(
            spec, current_class, target.module_name, target.class_name,
            rejection_feedback=red_feedback, existing_tests=existing_tests,
            interface_contract=format_interface_contract(action_manifest, target.class_name), other_rules=other_rules)
        lint_ok, lint_reason = lint_red_test(test_code, require_both_sides=bool(spec.is_mathematical_boundary))
        if not lint_ok:
            red_attempts.append({"attempt": red_attempt, "approved": False, "reason": lint_reason})
            red_feedback = _sent_back(lint_reason, test_code)
            continue

        with open(test_file_path, "w", encoding="utf-8") as f:
            f.write(test_code)

        # 5-line Hash Lock: snapshot the approved test file's hash before the GREEN phase
        initial_test_hash = compute_test_file_hash(test_file_path)

        red_result = run_isolated_pytest(test_file_path, cwd=workspace_dir)
        red_eval = evaluate_red_gate_result(red_result["exit_code"], red_result.get("report"), red_result.get("stderr"))
        already_satisfied = False
        if red_eval.get("status") == "REJECTED_TAUTOLOGY":
            # A test that passes at once either asserts nothing, or tests a rule an earlier step already implemented
            # (the action stage writes the methods first). Run against the class with its behaviour emptied out, the
            # second kind fails (service_layer/hollow_check.py).
            if fails_without_behaviour(test_file_path, workspace_dir, target.domain_file, target.class_name,
                                       run=run_isolated_pytest, judge=evaluate_red_gate_result):
                red_eval = {"status": "ALREADY_SATISFIED", "approved": True,
                            "reason": "The class already enforces this rule: the test passes as it is and fails once "
                                      "the class's methods do nothing. No code was needed."}
                already_satisfied = True
            else:
                red_eval["reason"] += " It also passes when the class's methods do nothing, so it asserts no behaviour."
        red_attempts.append({"attempt": red_attempt, "approved": red_eval["approved"], "reason": red_eval.get("reason")})
        if red_eval["approved"]:
            return RedOutcome("already_satisfied" if already_satisfied else "approved", test_file_path, test_code,
                              initial_test_hash, red_result, red_eval, red_attempts)
        if red_eval.get("status") == "REJECTED_DOMAIN_BROKEN":
            # Regenerating the test cannot help: the domain module itself does not import. Fail loudly now.
            return RedOutcome("domain_broken", test_file_path, test_code, initial_test_hash, red_result, red_eval, red_attempts)
        red_feedback = _sent_back(f"{red_eval.get('reason')}\n{summarize_pytest_failure(red_result)}", test_code)

    if os.path.exists(test_file_path):  # a test rejected twice is known to be broken: do not keep it
        os.remove(test_file_path)
    return RedOutcome("rejected", test_file_path, test_code, "", red_result, red_eval, red_attempts)


def red_dead_end(spec: BusinessSpec, red: RedOutcome, workspace_dir: str) -> Optional[Dict[str, Any]]:
    """The spec's result when its RED phase settles it without a GREEN phase, else None."""
    common = {"spec_id": spec.spec_id, "red_attempts": red.attempts, "test_source": red.test_code}
    if red.verdict == "already_satisfied":
        # Nothing to write: the test stays in tests/unit as the rule's regression guard
        return {"success": True, "status": "FULFILLED", "phase": "COMMITTED", "test_file": red.test_file_path,
                "red_eval": red.evaluation, "attempts": [], "already_satisfied": True, **common}
    if red.verdict == "rejected":
        return {"success": False, "status": "REQUIRES_HUMAN_INTERVENTION", "phase": "RED_GATE",
                "error": red.attempts[-1]["reason"], **common}
    if red.verdict == "domain_broken":
        # The test itself was never judged, so keep it for a human instead of letting it fail the regression suite.
        return {"success": False, "status": "REQUIRES_HUMAN_INTERVENTION", "phase": "RED_GATE",
                "error": red.attempts[-1]["reason"], "pending_test": _quarantine_test(red.test_file_path, workspace_dir),
                **common}
    return None


@traced("tdd.run_loop")
def execute_spec_tdd_loop(spec: BusinessSpec, workspace_dir: str, action_manifest: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Synchronous flat TDD loop execution:
    RED -> GREEN (with LibCST micro-context extraction) -> Hash Lock Anti-Cheat -> COMMIT.
    """
    state = TddExecutionState(spec=spec)
    state.advance_to_red()

    target = locate_domain_target(spec, workspace_dir)
    target_class, domain_file, tests_dir = target.class_name, target.domain_file, target.tests_dir
    test_file_path = spec_test_path(spec, tests_dir)
    existing_tests = collect_existing_tests(tests_dir, exclude=test_file_path, module_name=target.module_name)

    red = run_red_phase(spec, target, workspace_dir, existing_tests, action_manifest)
    settled = red_dead_end(spec, red, workspace_dir)
    if settled is not None:
        state.phase = settled["phase"] if settled["success"] else "DEAD_END"
        state.status = settled["status"]
        return settled
    test_code, red_result, red_eval, red_attempts, initial_test_hash = (
        red.test_code, red.result, red.evaluation, red.attempts, red.test_hash)

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

    # Retry policy (.claude/rules/pipeline.md, retry policy): at most ONE retry, and only because the GREEN gate (or the merge of the
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
                existing_tests=existing_tests,
                module_helpers=module_helpers_source(domain_source, target_class)
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
                    regression = run_isolated_pytest(tests_dir, cwd=workspace_dir, timeout_seconds=REGRESSION_TIMEOUT_S)
                    if regression.get("timed_out"):
                        # Not a verdict on the code: the suite never answered, so there is nothing to feed back
                        rollback()
                        return {
                            "success": False,
                            "status": "REQUIRES_HUMAN_INTERVENTION",
                            "phase": "REGRESSION_GATE",
                            "spec_id": spec.spec_id,
                            "error": f"The regression suite (tests/unit) did not finish within {REGRESSION_TIMEOUT_S} "
                                     f"seconds, so the change could not be verified.",
                            "red_attempts": red_attempts,
                            "test_source": test_code,
                            "attempts": attempts,
                            "rolled_back": True,
                            "pending_test": _quarantine_test(test_file_path, workspace_dir)
                        }
                    if regression["exit_code"] != 0:
                        broken = _failed_test_files(regression) or ["(unknown)"]
                        green_result = regression
                        green_eval = {
                            "status": "REJECTED_REGRESSION",
                            "approved": False,
                            "reason": f"Regression: your change makes earlier tests fail again: {', '.join(broken)}. Keep every existing behavior.",
                            "broke": _failed_test_files(regression)
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
                    "pending_test": pending,
                    # the tests of other specs the last change broke: this spec and those could not be kept together
                    "broke": list(green_eval.get("broke") or [])
                }

            failure_msg = (
                f"The previous GREEN attempt was rejected: {green_eval.get('reason')}\n"
                + summarize_pytest_failure(green_result)
            )
    except BaseException:
        rollback()
        _quarantine_test(test_file_path, workspace_dir)
        raise
