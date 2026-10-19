"""
Page tests: a rule is proved by a test that drives the running app in a browser (ADR-010).

- The harness (`tests/e2e/conftest.py`, from `templates/page_test_conftest.py.tmpl`) gives each test an API of its
  own with nothing saved, and a browser that reaches the page through an address where `/api/` is that API.
- A run changes no code and ends in one of three ways: pass, fail (an assertion did not hold, or the page offered no
  control the test could use) or broken (the test could not judge).
- A test is written once and stored with its rule. It is written again when the rule's text changed or the test was
  broken. A newly written test that does not pass goes back to its writer once, with what happened: to be written
  so that it can judge, or to be checked against the rule. That is the single retry (.claude/rules/pipeline.md).
"""

import ast
import json
import os
import re
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from onboarding.app_inventory import inventory_frontend
from pipeline_trace import traced

HARNESS = os.path.join("tests", "e2e", "conftest.py")
PARTS = os.path.join("tests", "e2e", "parts.py")  # the plan's parts as functions a test finds them through (page_parts.py)
_TEMPLATE = os.path.join(os.path.dirname(__file__), "templates", "page_test_conftest.py.tmpl")
RUN_TIMEOUT_S = 90
PASS, FAIL, BROKEN = "pass", "fail", "broken"
_EVIDENCE_LIMIT = 3000
_SEEN_LIMIT = 6000
_PAGE_FILES = (".tsx", ".jsx")
# The exceptions that are a verdict on the rule. Anything else that ends a test means the test could not judge.
_NOT_HELD = "AssertionError"
_NO_CONTROL = "TimeoutError"


class NoTest(RuntimeError):
    """The model gave no test (a provider or parse error). Never retried."""


@dataclass
class Verdict:
    status: str
    reason: Optional[str] = None
    evidence: str = ""
    control_not_found: bool = False  # the test waited for a control the page never offered: the test may be wrong
    seen: str = ""  # what the page had sent the app and what the app held when the test ended (a test that did not pass)

    @property
    def could_not_judge(self) -> bool:
        return self.status == BROKEN or self.control_not_found


@dataclass
class AppDescription:
    """What the test writer is shown of an app: how records are arranged, what the opened page reads out (roles
    and names as a browser found them, so that a control's name is seen and not guessed), and the plan the page was
    built from. A test is written from the plan, which says what the page is to do, and not from the page's source,
    which says how it happens to do it; the source is shown only where there is no plan (and to `rule_fix`, which
    changes it)."""
    api: str
    page: str
    rendered: str = ""
    plan: str = ""


def rule_text(rule: Dict[str, Any]) -> str:
    """The wording a test is written for; a test written for other wording is stale."""
    gwt = rule.get("given_when_then") or " ".join(
        f"{word} {rule[key]}" for word, key in (("Given", "given_clause"), ("When", "when_clause"),
                                                ("Then", "then_clause"), ("Unless", "unless_clause")) if rule.get(key))
    return " ".join(str(gwt).split())


def rule_id(rule: Dict[str, Any]) -> str:
    return str(rule.get("spec_id") or rule.get("id") or "")


def path_of_test(workspace_dir: str, spec_id: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", spec_id.lower()).strip("_")
    return os.path.join(workspace_dir, "tests", "e2e", f"test_{slug}.py")


def ensure_harness(workspace_dir: str) -> str:
    """Writes the engine's harness into the app (again, when it differs) and returns its path."""
    with open(_TEMPLATE, encoding="utf-8") as f:
        wanted = f.read()
    path = os.path.join(workspace_dir, HARNESS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    current = None
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            current = f.read()
    if current != wanted:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(wanted)
    return path


def ensure_parts(workspace_dir: str, plan: str) -> Optional[str]:
    """Writes the functions a test finds the plan's parts through beside the tests and returns their path; None
    when the plan names no part."""
    from onboarding.page_parts import locators_module, parts_of
    parts = parts_of(plan)
    if not parts:
        return None
    path = os.path.join(workspace_dir, PARTS)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(locators_module(parts))
    return path


def _one_line(text: str) -> Optional[str]:
    return next((line.strip()[:240] for line in (text or "").splitlines() if line.strip()), None)


def _raised(test: Dict[str, Any]) -> Optional[str]:
    """`<when>:<exception type>` as the harness reported it, e.g. `call:AssertionError`."""
    raised = (test.get("metadata") or {}).get("raised")
    return str(raised) if raised else None


def _seen(test: Dict[str, Any]) -> str:
    """What the harness noted when a test did not pass (`App.seen`), as text: each thing the page asked the app to
    change with the app's answer, and the test's records as the app held them at the end."""
    seen = (test.get("metadata") or {}).get("seen")
    if not isinstance(seen, dict):
        return ""

    def text(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False)

    calls = [f"{call.get('method')} {call.get('path')} {text(call.get('sent'))}\n"
             f"  answered {call.get('status')}: {text(call.get('answered'))}" for call in seen.get("calls") or []]
    held = [f"{collection}: {text(records)}" for collection, records in (seen.get("records") or {}).items()]
    return "\n".join(
        ["What the page asked the app to change, and what the app answered:"]
        + (calls or ["(the page asked the app to change nothing)"])
        + ["", "The records of the test as the app held them when the test ended:"]
        + (held or ["(the test arranged no record)"]))[:_SEEN_LIMIT]


def judge(result: Dict[str, Any]) -> Verdict:
    """What a pytest run of one rule's test says about the rule (pure)."""
    if result.get("timed_out"):
        return Verdict(BROKEN, _one_line(result.get("stderr", "")) or "the test timed out", result.get("stderr", ""))
    report = result.get("report") or {}
    failed_imports = [str(c.get("longrepr") or "") for c in report.get("collectors", []) if c.get("outcome") == "failed"]
    if failed_imports:
        text = "\n".join(failed_imports)
        errors = [line.strip() for line in text.splitlines() if line.strip().startswith("E ")]
        return Verdict(BROKEN, (errors[-1][1:].strip() if errors else _one_line(text)), text[-_EVIDENCE_LIMIT:])
    tests = report.get("tests") or []
    if not tests:
        said = (result.get("stderr") or result.get("stdout") or "").strip()
        return Verdict(BROKEN, _one_line(said) or "the run collected no test", said[-_EVIDENCE_LIMIT:])

    not_held: List[Verdict] = []
    for test in tests:
        if test.get("outcome") == "passed":
            continue
        stage = next((test[when] for when in ("setup", "call", "teardown")
                      if (test.get(when) or {}).get("outcome") == "failed"), {})
        message = str((stage.get("crash") or {}).get("message") or "")
        # The crash message opens with what was expected; a traceback ends in whatever was printed last
        case = str(test.get("nodeid") or "").rsplit("::", 1)[-1]
        evidence = (f"in {case}:\n" + condense(message or str(stage.get("longrepr") or "")))[:_EVIDENCE_LIMIT]
        raised = _raised(test) or ""
        if raised in (f"call:{_NOT_HELD}", f"call:{_NO_CONTROL}"):
            not_held.append(Verdict(FAIL, _one_line(message) or raised, evidence, raised.endswith(_NO_CONTROL),
                                    seen=_seen(test)))
        else:
            return Verdict(BROKEN, _one_line(message) or raised or f"the test ended as {test.get('outcome')}", evidence,
                           seen=_seen(test))
    if not not_held:
        return Verdict(PASS)
    # An assertion that did not hold says more than a control that was not found
    return next((v for v in not_held if not v.control_not_found), not_held[0])


def lint(source: str) -> "tuple[bool, str]":
    """Cheap checks before a browser starts: the module is a page test that asserts something."""
    try:
        tree = ast.parse(source)
    except SyntaxError as err:
        return False, f"SyntaxError in the test: {err}"
    tests = [n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name.startswith("test_")]
    if not tests:
        return False, "The module defines no test function (a function whose name starts with test_)."
    for node in ast.walk(tree):
        names = [node.module or ""] if isinstance(node, ast.ImportFrom) else (
            [alias.name for alias in node.names] if isinstance(node, ast.Import) else [])
        if any(name == "src" or name.startswith("src.") for name in names):
            return False, ("The test has an import from the app's own code. A page test knows the app only through its "
                           "page and its API: use the `app` fixture.")
    if "app.open(" not in source:
        return False, "The test never calls app.open(): the When of a rule is done on the page, as a person would."
    if not any(isinstance(n, ast.Assert) for n in ast.walk(tree)) and "expect(" not in source:
        return False, "The test checks nothing: it has no assert statement and no expect(...)."
    return True, ""


def _stored_test_still_fits(rule: Dict[str, Any], stored: Optional[Dict[str, Any]]) -> bool:
    return bool(stored and stored.get("source") and stored.get("status") in (PASS, FAIL)
                and stored.get("written_for") == rule_text(rule))


def _outcome(rule: Dict[str, Any], verdict: Verdict, source: Optional[str], written: int) -> Dict[str, Any]:
    return {"status": verdict.status, "reason": verdict.reason, "evidence": verdict.evidence, "seen": verdict.seen,
            "source": source, "written_for": rule_text(rule), "written": written}


def prove(rule: Dict[str, Any], write: Callable[[Dict[str, Any], str], str], run: Callable[[str], Verdict],
          stored: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Runs the rule's test and returns what to store: status, reason, evidence, the test and how often it was
    written in this call. `write(rule, feedback)` returns a test's source or raises NoTest; `run(source)` runs it."""
    if _stored_test_still_fits(rule, stored):
        source = str((stored or {})["source"])
        return _outcome(rule, run(source), source, 0)

    feedback, source, verdict = "", None, Verdict(BROKEN, "no test was written")
    for written in (1, 2):
        previous = source
        try:
            source = write(rule, feedback)
        except NoTest as err:
            return _outcome(rule, Verdict(BROKEN, str(err), str(err)), previous, written)
        if previous is not None and source.strip() == previous.strip():
            return _outcome(rule, verdict, source, written)  # the writer stands by its test: the first verdict stands
        accepted, why = lint(source)
        verdict = run(source) if accepted else Verdict(BROKEN, why, why)
        if verdict.status == PASS:
            break
        feedback = _feedback(source, verdict)
    return _outcome(rule, verdict, source, written)


def _feedback(source: str, verdict: Verdict) -> str:
    """What the writer is told about a new test that did not pass, for its one second attempt."""
    shown = f"```python\n{source}\n```\nWhat happened when it ran:\n```\n{verdict.evidence or verdict.reason}\n```\n"
    if verdict.could_not_judge:
        return ("\n## Your previous test could not judge the rule\n" + shown +
                "Write the test again so that it can judge the rule. If a control the test waited for is not on the "
                "page under that role and name, find the control by the role and name it is shown to carry "
                "above.\n")
    return ("\n## Your previous test ran and an assertion did not hold\n" + shown +
            "Either the app does not keep the rule, or the test expects something the rule does not say for the "
            "records it arranged. Go through the test once more against the rule: are the arranged records what the "
            "Given describes, complete and consistent with each other; does each position, count and name in an "
            "assertion follow from them; is every expectation something the rule states? If you find a mistake in "
            "the test, answer with the corrected test. If the test is right, answer with the same test, unchanged: "
            "the app is then what is wrong. The rule decides what is expected. What the app did is never a reason "
            "to expect it.\n")


# ── what the test writer is shown ────────────────────────────────────────────

def _api_of(workspace_dir: str) -> str:
    from onboarding.cst_isolator import extract_class_cst
    from service_layer.tdd_machine import summarize_class_api
    routers = os.path.join(workspace_dir, "src", "entrypoints", "routers")
    parts: List[str] = []
    for name in sorted(os.listdir(routers)) if os.path.isdir(routers) else []:
        if not name.endswith(".py") or name.startswith("_"):
            continue
        with open(os.path.join(routers, name), encoding="utf-8") as f:
            router = f.read()
        prefix = re.search(r'APIRouter\(\s*prefix\s*=\s*"/api/([^"]+)"', router)
        owner = re.search(r"from src\.domain\.(\w+) import (\w+)", router)
        if not prefix or not owner:
            continue
        module = os.path.join(workspace_dir, "src", "domain", f"{owner.group(1)}.py")
        try:
            with open(module, encoding="utf-8") as f:
                described = summarize_class_api(extract_class_cst(f.read(), owner.group(2)))
        except Exception as err:  # the class is shown as far as it can be read; the test's run says the rest
            described = f"# {owner.group(2)} could not be read: {err}"
        parts.append(f"### Collection `{prefix.group(1)}`: records of {owner.group(2)}\n```python\n{described}\n```")
    return "\n\n".join(parts)


def page_files(workspace_dir: str) -> Dict[str, str]:
    """The files the page is made of (the views and components it serves), by path, with their source."""
    files: Dict[str, str] = {}
    for source in inventory_frontend(workspace_dir).files:
        if not source.reachable or not source.path.endswith(_PAGE_FILES) or source.path.endswith("main.tsx"):
            continue
        with open(os.path.join(workspace_dir, *source.path.split("/")), encoding="utf-8") as f:
            files[source.path] = f.read()
    return files


def _page_of(workspace_dir: str) -> str:
    return "\n\n".join(f"### {path}\n```tsx\n{code.rstrip()}\n```" for path, code in page_files(workspace_dir).items())


_LIKE_CONTROL = re.compile(r'^(\s*)- (\w+) "([^"]*\d[^"]*)"')
_RUN_KEPT, _RUN_WORTH_CONDENSING, _KINDS_NAMED = 3, 8, 6


def condense(listing: str) -> str:
    """A long run of like controls (same place, same role, names that differ in their numbers) is shown by its first
    few and one line that counts the rest and gives each kind of name they carry. A grid of four hundred cells
    then costs the reader a handful of lines, and still shows every form a cell's name takes."""
    def like(line: str):
        found = _LIKE_CONTROL.match(line)
        return (found.group(1), found.group(2), re.split(r"\d", found.group(3), 1)[0]) if found else None

    lines, kept, at = listing.split("\n"), [], 0
    while at < len(lines):
        key, end = like(lines[at]), at + 1
        while key and end < len(lines) and like(lines[end]) == key:
            end += 1
        if end - at <= _RUN_WORTH_CONDENSING:
            kept.extend(lines[at:end])
        else:
            rest = lines[at + _RUN_KEPT:end]
            kinds = sorted({re.sub(r"\d+", "#", _LIKE_CONTROL.match(line).group(3)) for line in rest})
            named = " or ".join(f'"{kind}"' for kind in kinds[:_KINDS_NAMED]) + (" and others" if len(kinds) > _KINDS_NAMED else "")
            kept.extend(lines[at:at + _RUN_KEPT])
            kept.append(f"{key[0]}- … {len(rest)} more {key[1]} like these, named {named}")
        at = end
    return "\n".join(kept)


_READ_OUT_ID = "page as it opens"
_READ_OUT_FILE = os.path.join("tests", "e2e", ".page_as_it_opens.txt")
_READ_OUT = '''"""Written by the engine: reads out what the page offers when it opens, for the writer of the page tests."""
import os


def test_the_page_opens(app):
    page = app.open()
    page.wait_for_load_state("networkidle")
    with open(os.path.join(os.path.dirname(__file__), ".page_as_it_opens.txt"), "w", encoding="utf-8") as f:
        f.write(page.locator("body").aria_snapshot())
'''


@traced("page_test.read_out")
def read_out_page(workspace_dir: str, page_url: str) -> str:
    """What the page reads out when it opens on an app that holds only what it starts with, through the same
    harness the tests use. A page that cannot be opened is said so here; every test's run will say it too."""
    verdict = run_test(workspace_dir, _READ_OUT_ID, _READ_OUT, page_url)
    if verdict.status != PASS:
        return f"(the page could not be opened: {verdict.reason})"
    with open(os.path.join(workspace_dir, _READ_OUT_FILE), encoding="utf-8") as f:
        return condense(f.read())


_PLAN_STARTS, _PLAN_ENDS = "### 1. Opening", "### 6. Visual Direction"


def page_plan(specification: str) -> str:
    """The page's plan as a product's stored specification holds it (`ProductContract.blueprint()`): how the page
    opens, where each action is done, how each part is read out, its wordings and its refusals. The look that
    follows is left out, since no rule is told apart by a look. Empty when the specification holds no plan."""
    text = (specification or "").replace("\r\n", "\n")
    start = text.find(_PLAN_STARTS)
    if start < 0:
        return ""
    end = text.find(_PLAN_ENDS, start)
    return text[start:end if end >= 0 else len(text)].strip()


def _page_block(app: AppDescription) -> str:
    if app.plan:
        return ("## The page's plan\nWhat the page was built from: how it opens, where each action is done, the role "
                "and name each part is read out by (a value in braces is filled in from the record shown), its "
                "wordings, and the sentence shown when something is refused.\n\n" + app.plan)
    return "## The page's source\n" + app.page


def describe_app(workspace_dir: str, page_url: Optional[str] = None,
                 read_out: Optional[Callable[[str, str], str]] = None, plan: str = "") -> AppDescription:
    rendered = (read_out or read_out_page)(workspace_dir, page_url) if page_url else ""
    return AppDescription(api=_api_of(workspace_dir), page=_page_of(workspace_dir), rendered=rendered, plan=plan)


# ── the model and the browser ────────────────────────────────────────────────

def _extract_python(raw: str) -> Optional[str]:
    match = re.search(r"```(?:python|py)?\s*\n(.*?)```", raw or "", re.DOTALL)
    return match.group(1).strip() + "\n" if match and match.group(1).strip() else None


@traced("page_test.write")
def write_test(rule: Dict[str, Any], app: AppDescription, feedback: str = "") -> str:
    """Has the model write the rule's page test."""
    import agent_orchestrator
    from onboarding.page_parts import locators_block, parts_of, shown_values
    prompt = agent_orchestrator.load_prompt("page_test_generation.md", {
        "parts_block": locators_block(parts_of(app.plan), shown_values(app.plan)),
        "title": rule.get("title", ""), "description": rule.get("description", ""), "rule": rule_text(rule),
        "api": app.api, "page_block": _page_block(app), "rendered": app.rendered, "feedback_block": feedback,
        "situation_block": f"\n- **Situation** {rule['situation']}" if rule.get("situation") else "",
    })
    raw = agent_orchestrator.call_gemini(prompt, stage="page_test_generation")
    if not raw or not raw.strip():
        raise NoTest(agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response")
    source = _extract_python(raw)
    if source is None:
        raise NoTest("the answer contained no Python module")
    return source


@traced("page_test.run")
def run_test(workspace_dir: str, spec_id: str, source: str, page_url: str) -> Verdict:
    """Writes the rule's test into the app and runs it in a browser against the page at `page_url`."""
    from service_layer.tdd_machine import run_isolated_pytest
    ensure_harness(workspace_dir)
    path = path_of_test(workspace_dir, spec_id)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(source)
    result = run_isolated_pytest(os.path.relpath(path, workspace_dir).replace(os.sep, "/"), cwd=workspace_dir,
                                 timeout_seconds=RUN_TIMEOUT_S, extra_env={"PAGE_URL": page_url})
    return judge(result)


@traced("page_test.prove")
def prove_rule(rule: Dict[str, Any], workspace_dir: str, page_url: str, stored: Optional[Dict[str, Any]] = None,
               app: Optional[AppDescription] = None, plan: str = "") -> Dict[str, Any]:
    """`prove` with the model writing and a browser running."""
    described: List[AppDescription] = [app] if app else []
    # a stored test finds the plan's parts through them as well; a run of every rule hands the plan over with the app
    ensure_parts(workspace_dir, plan or (app.plan if app else ""))

    def write(the_rule: Dict[str, Any], feedback: str) -> str:
        if not described:  # only read when a test has to be written
            described.append(describe_app(workspace_dir, page_url, plan=plan))
        return write_test(the_rule, described[0], feedback)

    return prove(rule, write=write, run=lambda source: run_test(workspace_dir, rule_id(rule), source, page_url), stored=stored)
