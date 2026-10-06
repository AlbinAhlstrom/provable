"""
Spec consistency review: specs from one decomposition are implemented one by one on the same classes, and the TDD loop
only shows each spec the earlier verified tests. A pair of specs that demand opposite results therefore surfaces late, as
a regression dead end on whichever runs second. One LLM call over the whole set names such pairs up front so they are
reported with the kickstart. It reports; it never rewrites specs or retries (rule 03 section 4).
"""

import json
import re
from typing import Any, Dict, List, Optional

import agent_orchestrator
from onboarding.intent import ProductIntent, intent_block
from onboarding.router_engine import BusinessSpec
from pipeline_trace import traced


@traced("engine.spec_review")
def review_spec_consistency(specs: List[BusinessSpec], intent: Optional[ProductIntent] = None) -> Dict[str, Any]:
    """Returns {"success": True, "conflicts": [{"specs": [...], "reason": str}]} or {"success": False, "error": str}."""
    if len(specs) < 2:
        return {"success": True, "conflicts": []}
    specs_block = "\n".join(f"- {s.spec_id} [{s.title}] ({s.target_aggregate}): {s.given_when_then}" for s in specs)
    prompt = agent_orchestrator.load_prompt("spec_consistency_review.md", {
        "intent_block": intent_block(intent), "specs_block": specs_block})
    raw = agent_orchestrator.call_gemini(prompt, stage="spec_consistency_review", json_mode=True)
    if not raw or not raw.strip():
        return {"success": False, "error": agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response"}
    try:
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip())
        conflicts = json.loads(text).get("conflicts")
        if not isinstance(conflicts, list):
            raise ValueError("no 'conflicts' list")
        known = {s.spec_id for s in specs}
        clean = [{"specs": [i for i in c.get("specs", []) if i in known], "reason": str(c.get("reason", ""))}
                 for c in conflicts if isinstance(c, dict)]
        return {"success": True, "conflicts": [c for c in clean if len(c["specs"]) >= 2]}
    except Exception as e:
        return {"success": False, "error": f"the review was not valid JSON: {e}"}
