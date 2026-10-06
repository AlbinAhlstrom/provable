"""
Action Protocol Synthesizer: designs the user-facing action contract between the domain and the UI.

The aggregate's domain class is owned by the skeleton (a plain dataclass) and evolved spec by spec by the TDD
loop, and the generated API already exposes every public domain method through the deterministic
`POST /api/<aggregates>/{id}/action` endpoint (see skeleton_builder.generate_router_module). This step therefore
writes NO code: one LLM call names the actions the UI should offer (the domain methods the specs call for) and
their parameters, so the presentation layer and the domain agree on names before the methods exist.
"""

import json
import os
import re
import time
from typing import Any, Dict, List

import agent_orchestrator
from typing import Optional
from onboarding.intent import ProductIntent, intent_block
from onboarding.router_engine import BusinessSpec, DomainStructureSchema
from onboarding.skeleton_builder import to_snake_case
from pipeline_trace import traced


def _sanitize_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "", name)


def _extract_json_payload(raw_response: str) -> Dict[str, Any]:
    text = raw_response.strip()
    if "```json" in text:
        text = text.split("```json", 1)[1].split("```", 1)[0].strip()
    elif "```" in text:
        text = text.split("```", 1)[1].split("```", 1)[0].strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        raise


def _read_domain_class(workspace_dir: str, class_name: str) -> str:
    path = os.path.join(workspace_dir, "src", "domain", f"{to_snake_case(class_name)}.py")
    if not os.path.exists(path):
        return f"# (no domain module written yet for {class_name})"
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


@traced("engine.action_protocol")
def synthesize_action_protocol(
    pitch: str,
    structure: DomainStructureSchema,
    inbox_specs: List[BusinessSpec],
    workspace_dir: str,
    intent: Optional[ProductIntent] = None,
) -> Dict[str, Any]:
    """Asks the LLM for the action manifest. Writes no files. On any failure returns success False with the reason."""
    start_time = time.time()
    master = next((e for e in structure.entities if e.is_aggregate_root), None) or (structure.entities[0] if structure.entities else None)
    master_name = _sanitize_name(master.name) if master else _sanitize_name(structure.domain_name or "Application")

    classes_block = "\n\n".join(
        f"# {e.name}\n```python\n{_read_domain_class(workspace_dir, e.name)}\n```" for e in structure.entities
    ) or "(no entities)"
    specs_block = "\n".join(
        f"- [{s.title}] ({s.target_aggregate}): {s.given_when_then}" for s in inbox_specs
    ) or "- (no behavioural specs yet)"

    prompt = agent_orchestrator.load_prompt("domain_engine_synthesis.md", {
        "pitch": pitch,
        "master_name": master_name,
        "domain_classes": classes_block,
        "bdd_section": specs_block,
        "intent_block": intent_block(intent),
    })
    raw = agent_orchestrator.call_gemini(prompt, stage="domain_engine_synthesis", json_mode=True)
    elapsed = lambda: round(time.time() - start_time, 2)  # noqa: E731
    if not raw or not raw.strip():
        reason = agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response"
        print(f"[Compiler:Node2] Action protocol synthesis failed: {reason}", flush=True)
        return {"success": False, "error": reason, "files": [], "elapsed_seconds": elapsed(), "action_manifest": {"actions": []}}
    try:
        manifest = _extract_json_payload(raw).get("action_manifest")
    except Exception as e:
        print(f"[Compiler:Node2] Action protocol was not valid JSON: {e}", flush=True)
        return {"success": False, "error": f"not valid JSON: {e}", "files": [], "elapsed_seconds": elapsed(), "action_manifest": {"actions": []}}
    if not isinstance(manifest, dict) or not isinstance(manifest.get("actions"), list):
        return {"success": False, "error": "the answer has no action_manifest.actions list", "files": [],
                "elapsed_seconds": elapsed(), "action_manifest": {"actions": []}}

    print(f"[Compiler:Node2] Action protocol designed in {elapsed()}s: {[a.get('name') for a in manifest['actions']]}", flush=True)
    return {
        "success": True,
        "files": [],
        "elapsed_seconds": elapsed(),
        "master_name": master_name,
        "master_slug": to_snake_case(master_name),
        "action_manifest": manifest,
        "router_code": None,
    }
