"""
The gates a written page goes through: QA, then one visual review.

    QA            layout on three devices, forms, console, contrast, types, every part the plan names
                  (page_parts.py) and an opening that shows at least one of them (qa_opening_check.py); one rework with the defects as feedback
    visual review one look at QA's screenshots, repairs as class changes; only for a page that passed QA

Both a kickstart and a page rebuild (`page_rebuild.py`) end here, so a page is judged the same way however it came to
be written. It is judged as a new visitor meets it, through an API started afresh with nothing saved (fresh_page.py). Each gate keeps its own stage record and failure reason. The collaborators are injected so the order and
the hand-over between the gates are testable without a browser or an LLM.
"""

import contextlib
import os
import time
import run_options
from dataclasses import dataclass, field
from typing import Any, Callable, ContextManager, Dict, List, Optional

from onboarding.page_parts import field_wordings, missing_parts, parts_of
from run_recorder import stage_begin

@dataclass
class PageGates:
    """What the gates decided about a page."""
    qa: Optional[Dict[str, Any]] = None                            # the QA gate's verdict (qa_gate.run_qa_gate)
    failures: List[Dict[str, str]] = field(default_factory=list)   # gates that left something wrong on the page
    remarks: List[str] = field(default_factory=list)               # what the visual review saw and did not repair
    timings: Dict[str, float] = field(default_factory=dict)


def _sources(files: List[str]) -> List[str]:
    """The page's files as written; a page of several copies is read once per file name."""
    read: Dict[str, str] = {}
    for path in files:
        if os.path.basename(path) not in read and os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                read[os.path.basename(path)] = f.read()
    return list(read.values())


def run_page_gates(
    *,
    workspace_dir: str,
    pitch: str,
    presentation: Dict[str, Any],
    ux_blueprint: str,
    audit: Optional[Callable[[], Dict[str, Any]]] = None,
    rework: Optional[Callable[[List[str], List[str]], bool]] = None,
    gate: Optional[Callable[..., Dict[str, Any]]] = None,
    review: Optional[Callable[..., Dict[str, Any]]] = None,
    page: Optional[Callable[[str], ContextManager[Any]]] = None,
) -> PageGates:
    """Audits the page the presentation stage wrote (`presentation` is that stage's result), has its defects reworked
    once, and has a page that passed looked at once. `audit` renders and measures the page, `rework` is handed the
    defects, `gate` is the QA loop and `review` the visual review. Without `audit`, the page is rendered through `page`
    (fresh_page.fresh_page), opened at the first audit and kept for both gates."""
    with contextlib.ExitStack() as stack:
        return _judge(workspace_dir=workspace_dir, pitch=pitch, presentation=presentation, ux_blueprint=ux_blueprint,
                      audit=audit, rework=rework, gate=gate, review=review, page=page, stack=stack)


def _judge(*, workspace_dir: str, pitch: str, presentation: Dict[str, Any], ux_blueprint: str,
           audit: Optional[Callable[[], Dict[str, Any]]], rework: Optional[Callable[[List[str], List[str]], bool]],
           gate: Optional[Callable[..., Dict[str, Any]]], review: Optional[Callable[..., Dict[str, Any]]],
           page: Optional[Callable[[str], ContextManager[Any]]], stack: contextlib.ExitStack) -> PageGates:
    if gate is None:
        from onboarding.qa_gate import run_qa_gate as gate
    if review is None:
        from onboarding.visual_review import review_and_repair as review
    outcome = PageGates()
    last_audit: Dict[str, Any] = {}
    opened: Dict[str, Any] = {}

    def fresh() -> Any:
        if "page" not in opened:
            from onboarding.fresh_page import fresh_page
            opened["page"] = stack.enter_context((page or fresh_page)(workspace_dir))
        return opened["page"]

    def run_audit() -> Dict[str, Any]:
        if audit is not None:
            last_audit["report"] = audit()
        else:
            from onboarding.qa_auditor import run_responsive_qa_audit
            looked_at = fresh()
            last_audit["report"] = run_responsive_qa_audit(url=looked_at.url, save_screenshots=True,
                                                          workspace_dir=workspace_dir, api_ready_url=looked_at.api_ready_url,
                                                          parts=parts_of(ux_blueprint))
        absent = missing_parts(parts_of(ux_blueprint), _sources(presentation.get("files", [])),
                               field_wordings(ux_blueprint))
        if absent:  # a part the plan names and the page lacks is a defect like any other the audit finds
            report = last_audit["report"]
            report["defects"] = list(report.get("defects") or []) + absent
            report["passed"] = False
        return last_audit["report"]

    def run_rework(defects: List[str], console_errors: List[str]) -> bool:
        print(f"[QA] ⚠️ Defects: {defects} (console: {len(console_errors)} errors); one rework", flush=True)
        if rework is not None:
            return bool(rework(defects, console_errors))
        from onboarding.code_verifier import self_heal_presentation_suite
        healed = self_heal_presentation_suite(
            workspace_dir=workspace_dir, pitch=pitch, defects=defects, console_errors=console_errors,
            component_files=presentation.get("files", []), contract_files=presentation.get("contract_files", []),
            plan=ux_blueprint)
        if healed:
            time.sleep(1.0)  # the preview server picks the rewritten files up before the next audit
        return bool(healed)

    started = time.time()
    st = stage_begin("qa")
    try:
        outcome.qa = gate(audit=run_audit, rework=run_rework,
                          **({"max_rework_attempts": 0} if run_options.strict() else {}))
        st.note("verdict", outcome.qa["verdict"])
        st.note("rework_attempts", outcome.qa["attempts"])
        for warning in outcome.qa.get("warnings") or []:
            print(f"[QA] ⚠️ Warning: {warning}", flush=True)
        if outcome.qa.get("warnings"):
            st.note("warnings", outcome.qa["warnings"])
        if outcome.qa["passed"]:
            st.ok()
            print(f"[QA] ✓ Passed after {outcome.qa['attempts']} rework attempt(s).", flush=True)
        else:
            st.fail(f"QA verdict {outcome.qa['verdict']}: {outcome.qa['defects']}")
            print(f"[QA] ❌ FAILED ({outcome.qa['verdict']}): {outcome.qa['defects']}", flush=True)
    except Exception as err:  # the audit itself broke: reported as its own verdict, never retried
        outcome.qa = {"passed": False, "verdict": "audit_error", "attempts": 0, "defects": [], "console_errors": [],
                      "error": str(err)}
        st.fail(str(err))
        print(f"[QA] Audit error: {err}", flush=True)
    outcome.timings["6_qa_audit"] = round(time.time() - started, 2)

    # The page was written already styled, from the UX plan's visual direction. One look at the QA screenshots repairs
    # what looks wrong with class changes (visual_review.py); nothing is rewritten.
    started = time.time()
    st = stage_begin("visual_review")
    if not presentation.get("files"):
        st.skip("the presentation stage delivered no components to review")
    elif not outcome.qa.get("passed"):
        st.skip("the page did not pass QA")
    else:
        from onboarding.ux_planner import visual_direction
        from onboarding.visual_review import screenshots_from_audit, unresolved
        looked = review(
            workspace_dir=workspace_dir, pitch=pitch, visual_direction=visual_direction(ux_blueprint),
            component_files=presentation.get("files", []),
            screenshots=screenshots_from_audit(last_audit.get("report") or {}), audit=run_audit,
            settled=outcome.qa.get("reworked") or [])
        for key in ("verdict", "problems", "edits", "not_repaired", "claims", "attempts"):
            st.note(key, looked[key])
        # The page passed QA: it works and can be read on every device. What the review saw beyond that and
        # could not repair is a matter of looks, kept as a remark on the stage and not held against the build.
        # A review that could not look at all is a failure: it is never read as "the page is fine".
        if looked["verdict"] == "error":
            outcome.failures.append({"stage": "visual_review", "error": str(looked["error"])})
            st.fail(str(looked["error"]))
        else:
            left_on_page = unresolved(looked)
            if left_on_page:
                outcome.remarks = list(looked.get("not_repaired") or []) or [left_on_page]
                st.note("remarks", outcome.remarks)
            st.ok()
        print(f"[Visual review] {looked['verdict']} ({len(looked['problems'])} problem(s), "
              f"{sum(1 for e in looked['edits'] if e['applied'])} repair(s) applied)", flush=True)
    outcome.timings["7_visual_review"] = round(time.time() - started, 2)
    return outcome
