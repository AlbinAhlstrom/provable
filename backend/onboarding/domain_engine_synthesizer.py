"""
Domain Engine Synthesizer — Node 2 of the Deterministic Compiler Graph.
Synthesizes pure Python DDD domain model, invariant state rules, and FastAPI REST endpoints
in a single fast targeted LLM pass (<6 seconds).
"""

import os
import re
import json
import time
from typing import List, Dict, Any, Optional
from onboarding.router_engine import DomainStructureSchema, BusinessSpec
from agent_orchestrator import call_gemini


def _to_snake_case(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


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


def _ensure_typing_imports(code: str) -> str:
    """Ensures commonly used typing constructs (Any, Dict, List, Optional, Union, Tuple, Set, Callable) are imported if referenced."""
    if not code:
        return code
    common_types = ["Any", "Dict", "List", "Optional", "Union", "Tuple", "Set", "Callable"]
    needed = [t for t in common_types if re.search(r'\b' + t + r'\b', code)]
    if not needed:
        return code

    # Check if typing is imported
    import_match = re.search(r'from\s+typing\s+import\s+([^\n]+)', code)
    if import_match:
        existing = [item.strip() for item in import_match.group(1).split(",")]
        missing = [t for t in needed if t not in existing]
        if missing:
            new_import = f"from typing import {', '.join(existing + missing)}"
            code = code.replace(import_match.group(0), new_import, 1)
    else:
        code = f"from typing import {', '.join(needed)}\n" + code
    return code


def _extract_action_manifest(payload: Dict[str, Any], router_code: str) -> Dict[str, Any]:
    """
    Extracts or derives the authoritative Action Manifest contract from the payload or router code.
    Guarantees zero contract drift between Node 2 (DDD Backend) and Node 3 (Frontend View).
    """
    manifest = payload.get("action_manifest")
    if manifest and isinstance(manifest, dict) and "actions" in manifest:
        return manifest

    actions = []
    seen = set()

    # Regex search for string matches in router dispatch block
    if router_code:
        # Match: action_type == "..." or action_type == '...'
        for m in re.finditer(r"action_type\s*==\s*['\"]([a-zA-Z0-9_\-]+)['\"]", router_code):
            act = m.group(1).strip().lower()
            if act not in seen:
                seen.add(act)
                actions.append({"name": act, "aliases": [act], "params": ["x", "y"] if "params.get" in router_code else []})

        # Match: action_type in ("...", "...")
        for m in re.finditer(r"action_type\s*in\s*\(([^)]+)\)", router_code):
            group = m.group(1)
            items = [re.sub(r"['\"\s]", "", item).lower() for item in group.split(",") if item.strip()]
            if items:
                primary = items[0]
                if primary not in seen:
                    seen.add(primary)
                    actions.append({"name": primary, "aliases": items, "params": ["x", "y"] if "params.get" in router_code else []})

    if not actions:
        actions = [{"name": "execute", "aliases": ["execute", "trigger"], "params": []}]

    return {"actions": actions}


def synthesize_and_write_domain_engine(
    pitch: str,
    structure: DomainStructureSchema,
    inbox_specs: List[BusinessSpec],
    workspace_dir: str
) -> Dict[str, Any]:
    """
    Directly synthesizes and writes pure Python DDD domain modules and FastAPI REST routers.
    Returns dictionary with generated file paths, execution status, and the authoritative Action Manifest.
    """
    start_time = time.time()
    domain_name = _sanitize_name(structure.domain_name or "Application")
    domain_slug = _to_snake_case(domain_name)

    master_entity = None
    for ent in structure.entities:
        if ent.is_aggregate_root and master_entity is None:
            master_entity = ent
            break

    master_name = _sanitize_name(master_entity.name) if master_entity else domain_name
    master_slug = _to_snake_case(master_name)

    entity_summaries = []
    for ent in structure.entities:
        attr_desc = ", ".join(f"{a.name}: {a.type}" for a in ent.attributes)
        entity_summaries.append(f"- **{ent.name}** ({'Aggregate Root' if ent.is_aggregate_root else 'Entity'}): [{attr_desc}]")
    entities_block = "\n".join(entity_summaries) if entity_summaries else f"- **{master_name}**: Primary Aggregate Root"

    bdd_lines = []
    for idx, spec in enumerate(inbox_specs, 1):
        bdd_lines.append(f"- **Invariant {idx} [{spec.title}]** ({spec.target_aggregate}):\n  - {spec.given_when_then}")
    bdd_section = "\n".join(bdd_lines) if bdd_lines else "- Enforce domain validation invariants and valid state progression."

    provable_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    rel_ws = os.path.relpath(workspace_dir, provable_root).replace("\\", "/")

    # Load prompt template
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "domain_engine_synthesis.md")
    if not os.path.exists(prompt_path):
        prompt_template = """You are Provable's Principal DDD Backend Architect.
Build the pure Python domain model, invariant enforcement rules, and FastAPI REST endpoints for:
## Domain Specification
- **Product Pitch**: "{pitch}"
- **Domain Identity**: `{domain_name}`
- **Master Entity**: `{master_name}`
- **Entities & Attributes**:
{entities_block}
## Required Behavioral Invariants:
{bdd_section}
Technical Constraints:
1. Pure domain isolation in `src/domain/`
2. Single source of truth
3. FastAPI router at `src/entrypoints/routers/{master_slug}.py` defining `router = APIRouter(prefix="/api/{master_slug}s", tags=["{master_name}"])`
Respond STRICTLY with JSON:
{
  "action_manifest": {
    "actions": [{"name": "reveal", "aliases": ["primary_reveal"], "params": ["x", "y"]}]
  },
  "domain_rules_py": "<complete code for src/domain/rules.py>",
  "domain_state_py": "<complete code for src/domain/state.py>",
  "domain_aggregate_py": "<complete code for src/domain/{master_slug}.py>",
  "router_py": "<complete code for src/entrypoints/routers/{master_slug}.py>"
}
"""
    else:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()

    prompt = prompt_template
    replacements = {
        "{pitch}": pitch,
        "{domain_name}": domain_name,
        "{master_name}": master_name,
        "{master_slug}": master_slug,
        "{rel_workspace}": rel_ws,
        "{entities_block}": entities_block,
        "{bdd_section}": bdd_section
    }
    for k, v in replacements.items():
        prompt = prompt.replace(k, str(v))

    print(f"[Compiler:Node2] Synthesizing pure Python DDD domain model and FastAPI router...", flush=True)
    raw_response = call_gemini(prompt, stage="domain_engine_synthesis")
    created_files = []

    if not raw_response:
        print(f"[Compiler:Node2] ⚠️ LLM returned empty response for domain engine synthesis.", flush=True)
        return {
            "success": False,
            "files": [],
            "elapsed_seconds": round(time.time() - start_time, 2),
            "action_manifest": {"actions": []}
        }

    try:
        payload = _extract_json_payload(raw_response)
    except Exception as e:
        print(f"[Compiler:Node2] ⚠️ Failed to parse domain engine JSON: {e}", flush=True)
        return {
            "success": False,
            "files": [],
            "elapsed_seconds": round(time.time() - start_time, 2),
            "action_manifest": {"actions": []}
        }

    router_code = payload.get("router_py") or ""
    # Normalize any accidental aggregate module imports in router_code
    if router_code:
        router_code = re.sub(
            r'from\s+(\.\.\.domain|src\.domain|\.domain)\.aggregate\b',
            rf'from \1.{master_slug}',
            router_code
        )
        router_code = re.sub(
            r'from\s+aggregate\b',
            rf'from src.domain.{master_slug}',
            router_code
        )

    action_manifest = _extract_action_manifest(payload, router_code)

    aggregate_bridge_code = f'''"""
Backward-compatible aggregate re-export bridge.
Re-exports all symbols from the primary domain aggregate module ({master_slug}.py).
"""
from src.domain.{master_slug} import *
'''

    file_mapping = {
        os.path.join(workspace_dir, "src", "domain", "rules.py"): payload.get("domain_rules_py"),
        os.path.join(workspace_dir, "src", "domain", "state.py"): payload.get("domain_state_py"),
        os.path.join(workspace_dir, "src", "domain", f"{master_slug}.py"): payload.get("domain_aggregate_py"),
        os.path.join(workspace_dir, "src", "domain", "aggregate.py"): aggregate_bridge_code,
        os.path.join(workspace_dir, "src", "entrypoints", "routers", f"{master_slug}.py"): router_code,
    }

    for path, code in file_mapping.items():
        if code and code.strip():
            code = _ensure_typing_imports(code.strip())
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(code + "\n")
            created_files.append(path)

    elapsed = round(time.time() - start_time, 2)
    print(f"[Compiler:Node2] ✓ Synthesized {len(created_files)} domain engine files in {elapsed}s (Actions: {[a['name'] for a in action_manifest.get('actions', [])]})", flush=True)
    return {
        "success": True,
        "files": created_files,
        "elapsed_seconds": elapsed,
        "master_name": master_name,
        "master_slug": master_slug,
        "action_manifest": action_manifest,
        "router_code": router_code
    }

