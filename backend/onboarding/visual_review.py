"""Visual review: look at the rendered page once and repair only what looks wrong.

The presentation stage writes the page already styled, in the visual direction the UX plan chose. Rewriting every
component a second time to "polish" it cost as much as writing it. Instead one multimodal call looks at the QA
screenshots (whole page, desktop and phone) next to the component sources and names the problems a visitor would
notice. Each problem comes with a repair expressed as a class change: this class text, in this file, becomes that.

A repair is a surgical delta, applied here and not by the model:
- it reaches class attributes only, so it cannot change copy, structure or logic;
- class text holds class names only (no quotes, braces or code);
- the changed file must still compile, and the page must still pass the QA audit, or the files are put back.

One look. When the applier refuses a repair (the class text is not in the file, it holds more than class names, the
file no longer compiles), the refused repairs go back to the reviewer once with the reason, and its corrected repairs
are applied the same way: the one retry the policy allows, a verifier's verdict fed back (.claude/rules/pipeline.md).
Provider and parse errors are reported, not retried, and never read as "the page is fine". Whatever is not repaired
is listed in the result, and `unresolved()` turns it into the stage's failure: a problem a visitor would notice and
that is still on the page degrades the build by name.
"""

import os
import re
import time
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

import agent_orchestrator
from onboarding.seed_data import SEED_FILE
from onboarding.verification import compile_tsx
from pipeline_trace import traced

REVIEW_PROMPT = "visual_review.md"
REFUSED_PROMPT = "visual_review_refused.md"
MAX_PROBLEMS = 6
MAX_RECORDS_CHARS = 8000  # the records are context for one check; a very large seed is shown up to here

# Class text: Tailwind class names separated by spaces, including variants and arbitrary values. Nothing that could
# close the attribute or start an expression.
_CLASS_TEXT = re.compile(r"^[A-Za-z0-9 _\-:/\[\]().,%#!+*&']+$")
_CLASS_ATTRIBUTE = re.compile(r"\bclassName=")


@dataclass(frozen=True)
class ClassEdit:
    """One repair: in `file`, the class text `find` becomes `replace`, to fix `problem`."""
    problem: str
    file: str
    find: str
    replace: str


@dataclass(frozen=True)
class EditOutcome:
    problem: str
    file: str
    find: str
    replace: str
    applied: bool
    occurrences: int
    reason: str  # why it was not applied; "" when it was


def _class_spans(code: str) -> List[Tuple[int, int]]:
    """The (start, end) of every className value: the quoted string, or the whole `{...}` expression."""
    spans = []
    for match in _CLASS_ATTRIBUTE.finditer(code):
        start = match.end()
        if start >= len(code):
            continue
        if code[start] in "\"'":
            end = code.find(code[start], start + 1)
            if end > start:
                spans.append((start + 1, end))
        elif code[start] == "{":
            depth = 0
            for index in range(start, len(code)):
                depth += {"{": 1, "}": -1}.get(code[index], 0)
                if depth == 0:
                    spans.append((start + 1, index))
                    break
    return spans


def apply_class_edit(code: str, edit: ClassEdit) -> Tuple[str, int, str]:
    """Applies one edit inside class attributes. Returns (code, occurrences replaced, reason it was refused)."""
    if not (_CLASS_TEXT.match(edit.find or "") and _CLASS_TEXT.match(edit.replace or "")):
        return code, 0, "the edit must hold only class names"
    if edit.find.strip() == edit.replace.strip():
        return code, 0, "the edit changes nothing"
    # whole class tokens only: `p-2` must not match inside `p-20` or `sm:p-2`
    pattern = re.compile(r"(?<![\w\-:\[/.])" + re.escape(edit.find.strip()) + r"(?![\w\-\]/.:])")
    pieces, cursor, count = [], 0, 0
    for start, end in _class_spans(code):
        replaced, n = pattern.subn(edit.replace.strip(), code[start:end])
        pieces += [code[cursor:start], replaced]
        cursor, count = end, count + n
    if count == 0:
        return code, 0, f"the class text was not found in {edit.file}"
    return "".join(pieces) + code[cursor:], count, ""


def screenshots_from_audit(report: Dict[str, Any]) -> Dict[str, str]:
    """The whole-page screenshots of a QA audit to review: the desktop and the phone."""
    labels = {"Desktop": "desktop, 1280px wide", "Mobile": "phone, 375px wide"}
    shots = {}
    for device in report.get("device_results") or []:
        if device.get("device") in labels and device.get("full_page_screenshot"):
            shots[labels[device["device"]]] = device["full_page_screenshot"]
    return shots


def _read_review(raw: str) -> Tuple[List[Dict[str, Any]], List[str]]:
    """The visual problems and, separately, the statements about the business that no record carries."""
    answer = agent_orchestrator.extract_json_object(raw)
    problems = answer.get("problems")
    if not isinstance(problems, list) or not all(isinstance(p, dict) for p in problems):
        raise ValueError("the answer has no `problems` list of objects")
    claims = answer.get("claims") or []
    if not isinstance(claims, list):
        raise ValueError("`claims` is not a list")
    return problems[:MAX_PROBLEMS], [str(c).strip() for c in claims if str(c).strip()]


def _records_block(workspace_dir: str) -> str:
    """The seed records the page is served, so a claim written into the page can be told from content it loads."""
    path = os.path.join(workspace_dir, SEED_FILE)
    if not os.path.exists(path):
        return "(the page is served no records)"
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()[:MAX_RECORDS_CHARS]


def _sources_block(sources: Dict[str, str]) -> str:
    return "\n\n".join(f"--- FILE ({rel}) ---\n{code}" for rel, code in sources.items())


def unresolved(review: Dict[str, Any]) -> str:
    """What a review leaves on the page: the problems it saw and could not repair, or why its repairs were taken
    back. "" when nothing is left."""
    if review.get("verdict") == "reverted":
        return str(review.get("error") or "the repairs were taken back")
    return "; ".join(str(item) for item in review.get("not_repaired") or [])


def _apply_repairs(problems: List[Dict[str, Any]], sources: Dict[str, str], workspace_dir: str,
                   compile_check: Callable[[str, str], Tuple[bool, str]]) -> Tuple[Dict[str, str], List[EditOutcome], List[str]]:
    """Applies each problem's class change to `sources`. Returns the sources after the repairs, one outcome per
    repair, and the problems that came without a repair. A changed file that no longer compiles goes back to what it
    was in `sources`, with its repairs marked refused."""
    current = dict(sources)
    outcomes: List[EditOutcome] = []
    without_repair: List[str] = []
    for problem in problems:
        description = str(problem.get("problem") or "").strip()
        file, find, replace = problem.get("file"), problem.get("find"), problem.get("replace")
        if not (isinstance(file, str) and isinstance(find, str) and isinstance(replace, str)):
            without_repair.append(f"{description}: no class change can fix it")
            continue
        edit = ClassEdit(problem=description, file=file, find=find, replace=replace)
        if file not in current:
            reason, count = f"{file} is not one of the page's components", 0
        else:
            current[file], count, reason = apply_class_edit(current[file], edit)
        outcomes.append(EditOutcome(**asdict(edit), applied=not reason, occurrences=count, reason=reason))

    for rel in [r for r in current if current[r] != sources[r]]:
        compiles, verdict = compile_check(workspace_dir, current[rel])
        if not compiles:
            current[rel] = sources[rel]
            outcomes = [EditOutcome(**{**asdict(o), "applied": False, "occurrences": 0,
                                       "reason": f"the repaired file does not compile: {verdict}"})
                        if o.file == rel and o.applied else o for o in outcomes]
    return current, outcomes, without_repair


@traced("visual.review")
def review_and_repair(
    workspace_dir: str,
    pitch: str,
    visual_direction: str,
    component_files: List[str],
    screenshots: Dict[str, str],
    audit: Optional[Callable[[], Dict[str, Any]]] = None,
    llm: Optional[Callable[..., str]] = None,
    compile_check: Callable[[str, str], Tuple[bool, str]] = compile_tsx,
) -> Dict[str, Any]:
    """Looks at the page once and repairs what looks wrong with class changes.

    `screenshots` maps a label ("desktop", "phone") to an image file. `audit` re-checks the page after a repair; a
    failed audit puts every file back. Returns {verdict, problems, edits, not_repaired, claims, error, attempts,
    elapsed_seconds} with verdict one of clean | repaired | unrepaired | reverted | error. `attempts` is 2 when
    refused repairs were sent back to the reviewer. `claims` are statements
    about the business written into the page that no record carries: reported, since no class change removes one.
    """
    started = time.time()
    llm = llm or agent_orchestrator.call_gemini
    src_root = os.path.abspath(os.path.join(workspace_dir, "src"))
    paths = {os.path.relpath(os.path.abspath(p), workspace_dir).replace(os.sep, "/"): os.path.abspath(p)
             for p in component_files
             if p.endswith(".tsx") and not p.endswith("main.tsx") and os.path.abspath(p).startswith(src_root + os.sep)}
    originals: Dict[str, str] = {}
    for rel, path in paths.items():
        with open(path, "r", encoding="utf-8") as f:
            originals[rel] = f.read()

    def result(verdict: str, **extra: Any) -> Dict[str, Any]:
        base = {"verdict": verdict, "problems": [], "edits": [], "not_repaired": [], "claims": claims, "error": None,
                "attempts": attempts, "elapsed_seconds": round(time.time() - started, 2)}
        return {**base, **extra}

    claims: List[str] = []
    attempts = 1
    images = [path for path in screenshots.values() if path and os.path.exists(path)]
    if not images or not originals:
        return result("error", error="there is no screenshot or no component to review")

    def review_prompt(sources: Dict[str, str]) -> str:
        return agent_orchestrator.load_prompt(REVIEW_PROMPT, {
            "pitch": pitch, "visual_direction": visual_direction or "(no direction was planned)",
            "screenshots": ", ".join(f"image {i + 1}: {label}" for i, label in enumerate(screenshots)),
            "sources": _sources_block(sources), "records": _records_block(workspace_dir), "max_problems": MAX_PROBLEMS,
        })

    raw = llm(review_prompt(originals), stage="visual_review", json_mode=True, images=images)
    if not raw or not raw.strip():
        return result("error", error=agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response")
    try:
        problems, found = _read_review(raw)
        claims.extend(found)
    except Exception as exc:
        return result("error", error=f"the answer is not a usable review: {exc}")
    descriptions = [str(p.get("problem") or "").strip() for p in problems]
    if not problems:
        return result("clean")

    current, outcomes, not_repaired = _apply_repairs(problems, originals, workspace_dir, compile_check)

    # The one retry: repairs the applier refused go back to the reviewer with the reason, once
    refused = [o for o in outcomes if not o.applied]
    retry_error = ""
    if refused:
        attempts = 2
        feedback = "\n".join(f"- {o.problem}\n  file: {o.file}\n  find: {o.find}\n  replace: {o.replace}\n  refused: {o.reason}"
                             for o in refused)
        retry_prompt = review_prompt(current) + agent_orchestrator.load_prompt(REFUSED_PROMPT, {"refused": feedback})
        retry_raw = llm(retry_prompt, stage="visual_review", json_mode=True, images=images)
        try:
            if not retry_raw or not retry_raw.strip():
                raise ValueError(agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response")
            retry_problems, _ = _read_review(retry_raw)
        except Exception as exc:  # the first repairs stand; the refused ones stay refused, with this reason beside them
            retry_problems, retry_error = [], f"the corrected repairs could not be read: {exc}"
        current, corrected, no_repair = _apply_repairs(retry_problems, current, workspace_dir, compile_check)
        # The reviewer was asked for each refused problem once more, and may word it differently: every answer takes
        # the place of one refusal, so a refusal stays only when the retry gave no answer for it
        unanswered = refused[len(corrected) + len(no_repair):]
        outcomes = [o for o in outcomes if o.applied] + unanswered + corrected
        not_repaired += no_repair

    changed = [rel for rel in current if current[rel] != originals[rel]]
    not_repaired += [f"{o.problem}: {o.reason}" for o in outcomes if not o.applied]
    report = dict(problems=descriptions, edits=[asdict(o) for o in outcomes], not_repaired=not_repaired)
    if retry_error:
        report["error"] = retry_error
    if not changed:
        return result("unrepaired", **report)

    for rel in changed:
        with open(paths[rel], "w", encoding="utf-8") as f:
            f.write(current[rel])
    if audit is not None:
        time.sleep(1.0)  # let the dev server pick the files up
        final = audit()
        if not final.get("passed", False):
            for rel in changed:
                with open(paths[rel], "w", encoding="utf-8") as f:
                    f.write(originals[rel])
            defects = "; ".join(str(d) for d in final.get("defects") or []) or str(final.get("summary") or "audit failed")
            return result("reverted", **report, error=f"the repairs were taken back, the page no longer passed QA: {defects}",
                          final_audit=final)
        return result("repaired", **report, final_audit=final)
    return result("repaired", **report)
