"""
UX Interaction & Journey Planner — Step 5b.1 of the Deterministic Compiler Graph.
Reasons holistically about Cold Start defaults, information architecture,
action prerequisites, and human copy before presentation code synthesis.
"""

from pipeline_trace import traced
import os
import re
import time
from typing import Dict, Any, List, Optional
from onboarding.action_protocol import format_action_protocol
from onboarding.intent import ProductIntent, intent_block
from onboarding.router_engine import DomainStructureSchema, BusinessSpec
from agent_orchestrator import call_gemini


@traced("ux.plan_blueprint")
def plan_ux_blueprint(
    pitch: str,
    structure: DomainStructureSchema,
    action_manifest: Optional[Dict[str, Any]] = None,
    backend_state_model: str = "",
    master_name: str = "",
    master_slug: str = "",
    intent: Optional[ProductIntent] = None,
    inbox_specs: Optional[List[BusinessSpec]] = None
) -> str:
    """
    Synthesizes a structured UX Interaction Blueprint detailing cold start defaults,
    action prerequisites, form ergonomics, and copy harmonization.
    """
    start_time = time.time()
    domain_name = structure.domain_name or "Application"

    entity_summaries = []
    for ent in structure.entities:
        attr_desc = ", ".join(a.describe() for a in ent.attributes)
        role = f" ({ent.audience_role.value.replace('_', ' ')})" if ent.audience_role.value != "internal" else ""
        entity_summaries.append(f"- **{ent.name}**{role}: [{attr_desc}]")
    entities_block = "\n".join(entity_summaries) if entity_summaries else f"- **{master_name}**: Primary Aggregate Root"

    # The plan needs to know what the product does. With an action protocol that is its actions; planned alongside
    # the protocol (before it exists) it is the product's rules, from which the protocol is designed as well.
    if action_manifest:
        action_protocol_block = ("The backend domain engine provides these authoritative actions and state fields (the "
                                 "interface offers only the audience-facing ones; plan nothing for actions marked "
                                 "API-only):\n" + format_action_protocol(action_manifest))
    else:
        rules = "\n".join(f"- [{s.title}] ({s.target_aggregate}): {s.given_when_then}" for s in inbox_specs or [])
        action_protocol_block = ("The rules the product enforces (plan the audience's side of them; the business's own "
                                 "back-office handling is out of view):\n" + (rules or "- (no rules yet)"))

    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "ux_planning.md")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            template = f.read()
    else:
        template = "Plan UX for {pitch}"

    prompt = template.replace("{pitch}", pitch)
    prompt = prompt.replace("{domain_name}", domain_name)
    prompt = prompt.replace("{master_name}", master_name)
    prompt = prompt.replace("{entities_block}", entities_block)
    prompt = prompt.replace("{action_protocol_block}", action_protocol_block)
    prompt = prompt.replace("{intent_block}", intent_block(intent))

    print(f"[Compiler:UXPlanner] Reasoning about Cold Start, user journeys, and action ergonomics...", flush=True)
    try:
        blueprint = call_gemini(prompt, stage="ux_planning")
        if blueprint and len(blueprint.strip()) > 50:
            elapsed = round(time.time() - start_time, 2)
            print(f"[Compiler:UXPlanner] ✓ Synthesized UX Blueprint in {elapsed}s", flush=True)
            return blueprint.strip()
    except Exception as e:
        print(f"[Compiler:UXPlanner] Notice: {e}. Falling back to default UX flow.")

    return """### 1. Default Landing & Cold-Start Behavior
Show the product's primary view first, with a helpful empty state wherever a collection is empty.

### 2. Primary Navigation & View Structure
Keep navigation to the views the product intent calls for, ordered by what a first-time visitor needs.

### 3. Workflow Prerequisites & Form Ergonomics
Ensure all form inputs have visible descriptive labels. If prerequisites are missing, display explanatory notices.

### 4. Human Copy & Action Labeling
Use clear, approachable human terminology matching the audience. Avoid internal developer jargon."""


_DIRECTION_HEADING = "### 6. Visual Direction"


def visual_direction(blueprint: Optional[str]) -> str:
    """The visual direction section of a UX blueprint ("" when the blueprint has none)."""
    text = blueprint or ""
    start = text.find(_DIRECTION_HEADING)
    return text[start + len(_DIRECTION_HEADING):].strip() if start >= 0 else ""
