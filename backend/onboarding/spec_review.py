"""
Spec consistency review: specs from one decomposition are implemented one by one on the same classes, and the TDD loop
only shows each spec the earlier verified tests. A pair of specs that demand opposite results therefore surfaces late, as
a regression dead end on whichever runs second. One LLM call over the whole set names such pairs up front so they are
reported with the kickstart. It reports; it never rewrites specs or retries (.claude/rules/pipeline.md, retry policy).

A rule can also contradict the plan it was written with: it states an outcome the action, as the plan describes it,
does not have from the situation the rule starts from. Read as text, such a rule looks fine beside the others, and
both it and the rule it denies get a green test of the class alone. So the review is shown the plan's actions and
each rule's situation, and works every rule about an action through against the plan (`checked`) before it names
any conflict: asked for the verdict alone, a model names none here. One rule is reported against the plan only when
its check says it does not hold and a conflict names it. Measured on seven contracts, every real one had both, and
the one check marked as not holding without a conflict had worked out exactly what its rule states.
"""

import json
import re
from typing import Any, Dict, List, Optional

import agent_orchestrator
from onboarding.intent import ProductIntent, intent_block
from onboarding.router_engine import BusinessSpec
from pipeline_trace import traced

STAGE = "spec_consistency_review"
# Seconds the call may take: the answer works through every rule about an action, some 60 tokens each
REVIEW_TIMEOUT_S = 120.0
NO_ACTION = "### Specifications about no action of the plan"

_TEXT = {"type": "string"}
REVIEW_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "properties": {
        "checked": {"type": "array", "items": {
            "type": "object",
            "properties": {"spec": _TEXT, "closing": _TEXT, "leaves": _TEXT, "holds": {"type": "boolean"}},
            "required": ["spec", "closing", "leaves", "holds"]}},
        "conflicts": {"type": "array", "items": {
            "type": "object",
            "properties": {"specs": {"type": "array", "items": _TEXT}, "reason": _TEXT},
            "required": ["specs", "reason"]}},
    },
    "required": ["checked", "conflicts"],
}


def _line(spec: BusinessSpec) -> str:
    starts = f"\n  Starts from {spec.situation}" if getattr(spec, "situation", "") else ""
    return f"- {spec.spec_id} [{spec.title}] ({spec.target_aggregate}): {spec.given_when_then}{starts}"


def specs_block(specs: List[BusinessSpec], actions: Optional[Dict[str, str]] = None) -> str:
    """The specifications as the review reads them: under each action of the plan, as the plan describes it, the
    specifications about it; then those about none. Without a plan, one list."""
    if not actions:
        return "\n".join(_line(spec) for spec in specs)
    blocks = []
    for name, described in actions.items():
        about = [_line(spec) for spec in specs if getattr(spec, "action", "") == name]
        if about:
            blocks.append("\n".join([f"### {described}", *about]))
    rest = [_line(spec) for spec in specs if getattr(spec, "action", "") not in actions]
    if rest:
        blocks.append("\n".join([NO_ACTION, *rest]))
    return "\n\n".join(blocks)


def _conflicts(answer: Dict[str, Any], known: set) -> List[Dict[str, Any]]:
    """The conflicts of an answer: sets of two or more specs, and one spec alone when its check did not hold."""
    said = answer.get("conflicts")
    if not isinstance(said, list):
        raise ValueError("no 'conflicts' list")
    checks = [c for c in answer.get("checked") or [] if isinstance(c, dict) and c.get("spec") in known]
    unheld = {c["spec"] for c in checks if c.get("holds") is False}
    clean = [{"specs": [i for i in c.get("specs", []) if i in known], "reason": str(c.get("reason", ""))}
             for c in said if isinstance(c, dict)]
    return [c for c in clean if len(c["specs"]) >= 2 or (c["specs"] and c["specs"][0] in unheld)]


@traced("engine.spec_review")
def review_spec_consistency(specs: List[BusinessSpec], intent: Optional[ProductIntent] = None,
                            actions: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Returns {"success": True, "conflicts": [{"specs": [...], "reason": str}]} or {"success": False, "error": str}.
    `actions` is the plan's actions by name, each as the plan describes it; with it a conflict may name one spec,
    which then contradicts the plan."""
    if not specs or (len(specs) < 2 and not actions):
        return {"success": True, "conflicts": []}
    prompt = agent_orchestrator.load_prompt("spec_consistency_review.md", {
        "intent_block": intent_block(intent), "specs_block": specs_block(specs, actions)})
    raw = agent_orchestrator.call_gemini(prompt, stage=STAGE, json_mode=True, json_schema=REVIEW_SCHEMA,
                                         timeout_s=REVIEW_TIMEOUT_S)
    if not raw or not raw.strip():
        return {"success": False, "error": agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response"}
    try:
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
        return {"success": True, "conflicts": _conflicts(json.loads(text), {s.spec_id for s in specs})}
    except Exception as e:
        return {"success": False, "error": f"the review was not valid JSON: {e}"}
