"""
Presentation specs: specifications about what the user sees (a section, a layout, a visual state), as opposed to
behaviour specs, which the TDD loop proves with a RED test and a GREEN domain change.

A spec declares its own kind (`SpecKind`), decided by the decomposition step that understands it; there is no
keyword guessing here. A presentation spec is applied by rewriting the one view that belongs to its aggregate and
is verified by building the frontend. A failed build is fed back once (rule 03 section 4); if it still fails the
original file is restored and the spec reports REQUIRES_HUMAN_INTERVENTION with every attempt. FULFILLED therefore
means "the changed view compiles", never "a file was written".
"""

import os
import re
from typing import Any, Dict, List, Optional

import agent_orchestrator
from onboarding.router_engine import SpecKind
from onboarding.verification import run_workspace_build
from pipeline_trace import traced

MAX_ATTEMPTS = 2  # first attempt + one build-feedback retry


def spec_kind(spec: Dict[str, Any]) -> SpecKind:
    """The spec's declared kind. Rule-deck cards express it as card_type VIEW; everything undeclared is behaviour."""
    declared = str(spec.get("kind") or "").lower()
    if declared == SpecKind.PRESENTATION.value or str(spec.get("card_type") or "").upper() == "VIEW":
        return SpecKind.PRESENTATION
    return SpecKind.BEHAVIOR


def _view_path(workspace_dir: str, aggregate: str) -> str:
    name = re.sub(r"[^A-Za-z0-9_]", "", aggregate or "")
    return os.path.join(workspace_dir, "src", "views", f"{name}View.tsx")


def _extract_tsx(raw: str) -> Optional[str]:
    match = re.search(r"```(?:tsx|typescript|jsx|ts)?\s*\n(.*?)```", raw or "", re.DOTALL)
    code = match.group(1).strip() if match else ""
    return code if "export" in code else None


def _attempt(number: int, error: Optional[str]) -> Dict[str, Any]:
    """Same shape as the TDD loop's attempts, so the Studio renders them unchanged."""
    return {"attempt": number, "approved": error is None, "reason": error or "the view builds"}


def _result(status: str, files: List[str], attempts: List[Dict[str, Any]], error: Optional[str] = None) -> Dict[str, Any]:
    return {"success": status == "FULFILLED", "status": status, "phase": "presentation", "error": error,
            "files_updated": files, "attempts": attempts, "rolled_back": status != "FULFILLED" and bool(attempts)}


@traced("engine.presentation_spec")
def execute_presentation_spec(spec: Dict[str, Any], workspace_dir: str) -> Dict[str, Any]:
    """Applies a presentation spec to its aggregate's view and verifies it with a frontend build."""
    aggregate = spec.get("target_aggregate") or spec.get("target") or ""
    path = _view_path(workspace_dir, aggregate)
    shown = os.path.relpath(path, workspace_dir).replace(os.sep, "/")
    if not os.path.exists(path):
        return _result("REQUIRES_HUMAN_INTERVENTION", [], [], f"there is no view {shown} for aggregate '{aggregate}'")

    with open(path, "r", encoding="utf-8") as f:
        original = f.read()
    gwt = spec.get("given_when_then") or " ".join(
        c for c in (spec.get("given_clause"), spec.get("when_clause"), spec.get("then_clause")) if c)

    attempts: List[Dict[str, Any]] = []
    feedback = ""
    for number in range(1, MAX_ATTEMPTS + 1):
        prompt = agent_orchestrator.load_prompt("presentation_spec_evolution.md", {
            "title": spec.get("title", ""), "given_when_then": gwt, "file_path": shown,
            "current_code": original, "feedback_block": feedback,
        })
        raw = agent_orchestrator.call_gemini(prompt, stage="presentation_spec_evolution")
        if not raw or not raw.strip():
            reason = agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response"
            attempts.append(_attempt(number, reason))
            return _result("REQUIRES_HUMAN_INTERVENTION", [], attempts, reason)  # provider error: never retried
        code = _extract_tsx(raw)
        if code is None:
            attempts.append(_attempt(number, "the answer contained no complete TSX file"))
            return _result("REQUIRES_HUMAN_INTERVENTION", [], attempts, attempts[-1]["reason"])  # parse error: never retried

        with open(path, "w", encoding="utf-8") as f:
            f.write(code + "\n")
        build = run_workspace_build(workspace_dir)
        if build["ok"]:
            attempts.append(_attempt(number, None))
            return _result("FULFILLED", [path], attempts)
        attempts.append(_attempt(number, str(build["output"])[-2000:] or "the build failed"))
        feedback = f"\n## The previous attempt did not build\n```\n{attempts[-1]['reason']}\n```\nFix these errors.\n\n"

    with open(path, "w", encoding="utf-8") as f:
        f.write(original)
    return _result("REQUIRES_HUMAN_INTERVENTION", [], attempts, "the changed view did not build; the original was restored")
