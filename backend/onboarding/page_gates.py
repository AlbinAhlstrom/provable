"""
The gates a written page goes through: QA, then one visual review.

    QA            layout on three devices, forms, console, contrast, types; one rework with the defects as feedback
    visual review one look at QA's screenshots, repairs as class changes; only for a page that passed QA

Both a kickstart and a page rebuild (`page_rebuild.py`) end here, so a page is judged the same way however it came to
be written. Each gate keeps its own stage record and failure reason. The collaborators are injected so the order and
the hand-over between the gates are testable without a browser or an LLM.
"""

import time
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from run_recorder import stage_begin

PREVIEW_URL = "http://localhost:5174"
API_READY_URL = "http://localhost:8001/openapi.json"


@dataclass
class PageGates:
    """What the gates decided about a page."""
    qa: Optional[Dict[str, Any]] = None                            # the QA gate's verdict (qa_gate.run_qa_gate)
    failures: List[Dict[str, str]] = field(default_factory=list)   # gates that left something wrong on the page
    timings: Dict[str, float] = field(default_factory=dict)


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
) -> PageGates:
    """Audits the page the presentation stage wrote (`presentation` is that stage's result), has its defects reworked
    once, and has a page that passed looked at once. `audit` renders and measures the page, `rework` is handed the
    defects, `gate` is the QA loop and `review` the visual review."""
    if gate is None:
        from onboarding.qa_gate import run_qa_gate as gate
    if review is None:
        from onboarding.visual_review import review_and_repair as review
    outcome = PageGates()
    last_audit: Dict[str, Any] = {}

    def run_audit() -> Dict[str, Any]:
        if audit is not None:
            last_audit["report"] = audit()
        else:
            from onboarding.qa_auditor import run_responsive_qa_audit
            last_audit["report"] = run_responsive_qa_audit(url=PREVIEW_URL, save_screenshots=True,
                                                          workspace_dir=workspace_dir, api_ready_url=API_READY_URL)
        return last_audit["report"]

    def run_rework(defects: List[str], console_errors: List[str]) -> bool:
        print(f"[QA] ⚠️ Defects: {defects} (console: {len(console_errors)} errors); one rework", flush=True)
        if rework is not None:
            return bool(rework(defects, console_errors))
        from onboarding.code_verifier import self_heal_presentation_suite
        healed = self_heal_presentation_suite(
            workspace_dir=workspace_dir, pitch=pitch, defects=defects, console_errors=console_errors,
            component_files=presentation.get("files", []), contract_files=presentation.get("contract_files", []))
        if healed:
            time.sleep(1.0)  # the preview server picks the rewritten files up before the next audit
        return bool(healed)

    started = time.time()
    st = stage_begin("qa")
    try:
        outcome.qa = gate(audit=run_audit, rework=run_rework)
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
        # A problem the review saw and could not repair is still on the page: the build says so
        left_on_page = str(looked["error"]) if looked["verdict"] == "error" else unresolved(looked)
        if left_on_page:
            outcome.failures.append({"stage": "visual_review", "error": left_on_page})
            st.fail(left_on_page)
        else:
            st.ok()
        print(f"[Visual review] {looked['verdict']} ({len(looked['problems'])} problem(s), "
              f"{sum(1 for e in looked['edits'] if e['applied'])} repair(s) applied)", flush=True)
    outcome.timings["7_visual_review"] = round(time.time() - started, 2)
    return outcome
