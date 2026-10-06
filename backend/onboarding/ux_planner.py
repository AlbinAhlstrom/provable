"""
UX Interaction & Journey Planner — Step 5b.1 of the Deterministic Compiler Graph.
Reasons holistically about Cold Start defaults, information architecture,
action prerequisites, and human copy before presentation code synthesis.
"""

import os
import re
import time
from typing import Dict, Any, List, Optional
from onboarding.router_engine import DomainStructureSchema, BusinessSpec
from agent_orchestrator import call_gemini


def plan_ux_blueprint(
    pitch: str,
    structure: DomainStructureSchema,
    action_manifest: Optional[Dict[str, Any]] = None,
    backend_state_model: str = "",
    master_name: str = "",
    master_slug: str = ""
) -> str:
    """
    Synthesizes a structured UX Interaction Blueprint detailing cold start defaults,
    action prerequisites, form ergonomics, and copy harmonization.
    """
    start_time = time.time()
    domain_name = structure.domain_name or "Application"

    entity_summaries = []
    for ent in structure.entities:
        attr_desc = ", ".join(f"{a.name}: {a.type}" for a in ent.attributes)
        entity_summaries.append(f"- **{ent.name}**: [{attr_desc}]")
    entities_block = "\n".join(entity_summaries) if entity_summaries else f"- **{master_name}**: Primary Aggregate Root"

    protocol_lines = []
    if action_manifest and isinstance(action_manifest, dict) and "actions" in action_manifest:
        for act in action_manifest.get("actions", []):
            name = act.get("name", "action")
            params = ", ".join(f"`{p}`" for p in act.get("params", [])) or "None"
            desc = act.get("description", "")
            desc_part = f" — {desc}" if desc else ""
            protocol_lines.append(f"- Action `{name}`: params [{params}]{desc_part}")
    else:
        protocol_lines.append("- Action `dispatch`: standard domain actions")
    action_protocol_block = "\n".join(protocol_lines)

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
Default to primary customer intake/booking workflow when no active records exist. Render helpful empty states.

### 2. Primary Navigation & View Structure
Navigation follows natural lifecycle: 1. Overview/Showcase, 2. Intake/Booking, 3. Active Management.

### 3. Workflow Prerequisites & Form Ergonomics
Ensure all form inputs have visible descriptive labels. If prerequisites are missing, display explanatory notices.

### 4. Human Copy & Action Labeling
Use clear, approachable human terminology matching the personas. Avoid internal developer jargon."""
