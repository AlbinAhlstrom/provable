"""
Fixing a red rule (ADR-010): the page is changed so that the rule's own page test turns green.

- A fix starts from a test that judged the page and found it wanting (`fail`). A rule that never ran, passed or
  whose test is broken is not touched: there is nothing proven to fix.
- The writer is shown the rule, its test, what the test saw, the app's API and the page, and answers with whole
  files of the page. A file it was not shown is refused.
- A change is kept only when the app's check holds: the page builds, the rule's test passes, and every rule that
  was green is still green. A rejected change goes back once with what the check said; after a second rejection
  the page is as it was (.claude/rules/pipeline.md, retry policy).
- Only the page is changed here. A rule the domain class breaks is changed through the test-first loop, not here.
"""

import run_options
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional

from onboarding import page_tests
from pipeline_trace import traced

MAX_ATTEMPTS = 2  # first attempt + one retry with the check's verdict
FIXED, NOT_FIXED, NOT_RED = "fixed", "not_fixed", "not_red"
_EVIDENCE_LIMIT = 3000


class NoFix(RuntimeError):
    """The model gave no change (a provider or parse error). Never retried."""


@dataclass
class Check:
    """What the app said of a change: whether it holds, and when not, why."""
    ok: bool
    reason: str = ""
    evidence: str = ""


def _result(status: str, attempts: List[Dict[str, Any]], files: Optional[List[str]] = None,
            reason: Optional[str] = None) -> Dict[str, Any]:
    return {"status": status, "reason": reason, "files": files or [], "attempts": attempts}


def _refusal(change: Dict[str, str], pages: Dict[str, str]) -> Optional[str]:
    unknown = sorted(path for path in change if path not in pages)
    if unknown:
        return (f"the answer changes {', '.join(unknown)}, which is not part of the page; "
                f"the files that can be changed are {', '.join(sorted(pages))}")
    if all(pages[path] == code for path, code in change.items()):
        return "the answer changes nothing: every file in it is the file as it is now"
    return None


def _feedback(change: Dict[str, str], reason: str, evidence: str) -> str:
    tried = "\n\n".join(f"<<<{path}>>>\n{code}" for path, code in change.items())
    return ("## Your previous change was not kept\n"
            f"What you changed (the page is back as it was before this change):\n\n{tried}\n<<<end>>>\n\n"
            f"Why it was not kept: {reason}\n"
            + (f"\n```\n{evidence[:_EVIDENCE_LIMIT]}\n```\n" if evidence else "")
            + "\nChange the page again, starting from the files as they are shown above.\n")


def fix(rule: Dict[str, Any], stored: Optional[Dict[str, Any]], pages: Dict[str, str],
        write: Callable[[str], Dict[str, str]], put: Callable[[Dict[str, str]], None],
        check: Callable[[], Check]) -> Dict[str, Any]:
    """Has `write` change the page until `check` holds, at most twice. `pages` is the page as it is (path -> source);
    `put` writes files to the app, and is also how a rejected change is taken back."""
    if not stored or stored.get("status") != page_tests.FAIL:
        return _result(NOT_RED, [], reason="a fix starts from a rule whose test ran and failed")
    attempts: List[Dict[str, Any]] = []
    feedback, reason = "", None
    for number in range(1, run_options.attempts(MAX_ATTEMPTS) + 1):
        try:
            change = write(feedback)
        except NoFix as err:
            return _result(NOT_FIXED, attempts, reason=str(err))
        reason, evidence = _refusal(change, pages), ""
        if reason is None:
            put(change)
            verdict = check()
            if verdict.ok:
                attempts.append({"number": number, "files": sorted(change), "ok": True, "reason": None})
                return _result(FIXED, attempts, files=sorted(change))
            put({path: pages[path] for path in change})  # the page is as it was before the next attempt, or the end
            reason, evidence = verdict.reason, verdict.evidence
        attempts.append({"number": number, "files": sorted(change), "ok": False, "reason": reason})
        feedback = _feedback(change, reason, evidence)
    return _result(NOT_FIXED, attempts, reason=reason)


# ── the model, the disk and the app ──────────────────────────────────────────

@traced("rule_fix.write")
def write_fix(rule: Dict[str, Any], stored: Dict[str, Any], app: page_tests.AppDescription, feedback: str = "") -> Dict[str, str]:
    """Has the model change the page for a red rule. Returns the files it changed, whole."""
    import agent_orchestrator
    from onboarding.code_verifier import PresentationRepair
    prompt = agent_orchestrator.load_prompt("rule_fix.md", {
        "title": rule.get("title", ""), "rule": page_tests.rule_text(rule), "test": stored.get("source") or "",
        "reason": stored.get("reason") or "", "evidence": (stored.get("evidence") or "")[:_EVIDENCE_LIMIT],
        "api": app.api, "page": app.page, "feedback_block": feedback,
    })
    raw = agent_orchestrator.call_gemini(prompt, stage="rule_fix")
    if not raw or not raw.strip():
        raise NoFix(agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response")
    try:
        repair = PresentationRepair.from_response(raw)
    except ValueError as err:
        raise NoFix(str(err)) from None
    return {fix_.path: fix_.code + "\n" for fix_ in repair.fixes}


def check_app(workspace_dir: str, page_url: str, rule: Dict[str, Any], stored: Dict[str, Any],
              green: Dict[str, str], side_by_side: int = 6) -> Check:
    """The page builds, the rule's test passes, and every rule that was green (`green`: rule id -> its test) still is."""
    from concurrent.futures import ThreadPoolExecutor
    import pipeline_trace
    from onboarding.verification import run_workspace_build

    build = run_workspace_build(workspace_dir)
    if not build["ok"]:
        return Check(ok=False, reason="the page does not build", evidence=str(build["output"])[-_EVIDENCE_LIMIT:])
    own = page_tests.run_test(workspace_dir, page_tests.rule_id(rule), stored["source"], page_url)
    if own.status != page_tests.PASS:
        return Check(ok=False, reason=f"the rule's test still does not pass: {own.reason}", evidence=own.evidence)

    def one(item):
        other, source = item
        return other, page_tests.run_test(workspace_dir, other, source, page_url)

    with ThreadPoolExecutor(max_workers=min(side_by_side, max(1, len(green)))) as pool:
        verdicts = list(pool.map(pipeline_trace.bind_context(one), green.items()))
    broke = [(other, verdict) for other, verdict in verdicts if verdict.status != page_tests.PASS]
    if broke:
        told = "\n\n".join(f"{other}: {verdict.reason}\n{verdict.evidence[:600]}" for other, verdict in broke[:4])
        return Check(ok=False, reason=f"the change turned {len(broke)} rule(s) that were green red: "
                                      f"{', '.join(other for other, _ in broke)}", evidence=told)
    return Check(ok=True)


@traced("rule_fix.fix")
def fix_rule(rule: Dict[str, Any], stored: Optional[Dict[str, Any]], workspace_dir: str, page_url: str,
             green: Dict[str, str]) -> Dict[str, Any]:
    """`fix` with the model writing, the app's files on disk and its page tests as the check."""
    import os
    pages = page_tests.page_files(workspace_dir)
    described: List[page_tests.AppDescription] = []

    def write(feedback: str) -> Dict[str, str]:
        if not described:
            described.append(page_tests.describe_app(workspace_dir))
        return write_fix(rule, stored or {}, described[0], feedback)

    def put(files: Dict[str, str]) -> None:
        for path, code in files.items():
            with open(os.path.join(workspace_dir, *path.split("/")), "w", encoding="utf-8", newline="\n") as f:
                f.write(code)

    return fix(rule, stored, pages, write=write, put=put,
               check=lambda: check_app(workspace_dir, page_url, rule, stored or {}, green))
