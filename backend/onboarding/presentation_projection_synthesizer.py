"""
Presentation Projection Synthesizer — Node 3 of the Deterministic Compiler Graph.
Synthesizes the interactive presentation projection (React canvas, controls, history, API client, and <100 LOC App.tsx)
in a single fast targeted LLM pass (<6 seconds).
"""

from pipeline_trace import traced
import os
import re
import json
import time
from typing import List, Dict, Any, Optional
from onboarding import page_gestures, page_opening
from onboarding.action_protocol import format_action_protocol
from onboarding.intent import ProductIntent, intent_block
from onboarding import page_parts
from onboarding.page_parts import parts_block
from onboarding.router_engine import DomainStructureSchema, BusinessSpec
from onboarding.skeleton_builder import _pluralize
import agent_orchestrator
from agent_orchestrator import call_gemini


def _to_snake_case(name: str) -> str:
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _sanitize_name(name: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_]", "", name)


# The model answers with the four files as marker-delimited blocks, not as JSON string values: ~25k characters of
# escaped TSX inside one JSON object proved fragile (an object closed early and the remaining files were lost).
# Seconds the page call may take. It is the largest single answer of a build: 35 s on one model at low effort, past
# the 60 s of an ordinary call on another that thinks longer before it writes, and some 15,000 tokens at the 75 a
# second of a larger model is past 180 s.
PAGE_TIMEOUT_S = 300.0

SECTIONS = ("view_tsx", "controls_tsx", "history_tsx", "app_tsx")
PARTS = "parts"  # opens the answer: where the writer puts each part of the page (page_parts.py); a plan, not a file
END = "end"  # closes the answer: without a way to say "done" the model invents one, and it lands in the last file
_MARKER = re.compile(r"^<<<(\w+)>>>[ \t]*$", re.MULTILINE)


def _unfence(body: str) -> str:
    """A block may arrive wrapped in one markdown fence; the code is what is inside it."""
    lines = body.strip().splitlines()
    if lines and lines[0].startswith("```") and lines[-1].strip() == "```":
        lines = lines[1:-1]
    return "\n".join(lines).strip()


def parse_file_blocks(raw: str) -> Dict[str, str]:
    """Reads `<<<view_tsx>>>` ... `<<<app_tsx>>>` blocks. Raises ValueError naming what is wrong with the answer."""
    marks = list(_MARKER.finditer(raw or ""))
    if not marks:
        raise ValueError(f"no <<<section>>> markers in the answer; it began: {(raw or '')[:200]!r}")
    blocks: Dict[str, str] = {}
    for mark, following in zip(marks, marks[1:] + [None]):
        name = mark.group(1)
        if name == END:
            break
        if name == PARTS:
            continue
        if name not in SECTIONS:
            raise ValueError(f"unknown section <<<{name}>>> (expected {', '.join(SECTIONS)})")
        if name in blocks:
            raise ValueError(f"section <<<{name}>>> appears twice")
        blocks[name] = _unfence(raw[mark.end():following.start() if following else len(raw)])
    return blocks


_EXPORTED_BINDING = re.compile(r"\bexport\s+(?:default\b|const\b|function\b|class\b|let\b|var\b|\{\s*\w)")


def is_component_file(code: Optional[str]) -> bool:
    """A file block is a file only if it exports something. A module with no exports (`export {};`) is the model's way
    of saying "nothing here"; writing it would ship a component that nothing can import."""
    return bool(code and _EXPORTED_BINDING.search(code))


_ROLE_TEXT = {
    "created_by_audience": "the audience creates and works with these records (use `create{n}`)",
    "shown_to_audience": "shown to the audience: read-only content the business publishes (render `list{n}()`)",
    "internal": "internal",
}


def _clients_block(presented: List[Any], master_name: str, actions: Optional[List[Dict[str, Any]]] = None) -> str:
    """Describes every generated client the presentation may import, with each entity's role."""
    from onboarding.skeleton_builder import actions_export
    lines = []
    for ent in presented:
        n = _sanitize_name(ent.name)
        role = _ROLE_TEXT.get(getattr(ent.audience_role, "value", ent.audience_role), "internal").replace("{n}", n)
        if n == master_name:
            role = "the master: " + role if getattr(ent.audience_role, "value", None) == "created_by_audience" else "the master"
        # The page sends an action through its own function and is told of no other way (skeleton_builder)
        own = any(isinstance(a, dict) and a.get("aggregate") == n for a in actions or [])
        sending = (f" and `{actions_export(n)}` (one function per action of `{n}`, each called exactly as the action "
                   f"protocol above lists it; an action done to one record answers `Promise<{{ success: boolean; state: "
                   f"{n}State; created: {n}State | null; message?: string }}>`, `state` being that record afterwards; an "
                   f"action done to no one record answers `Promise<{{ success: boolean; created: {n}State | null; "
                   f"records: {n}State[]; message?: string }}>`, `created` being the record it made and `records` every "
                   f"stored `{n}` afterwards)") if own else ""
        needed = [a.name for a in ent.attributes if a.required and a.default_value is None and a.name != "id"]
        create_note = (f" (the server assigns `id`; the data must carry: {', '.join(f'`{a}`' for a in needed)}, with a "
                       f"value the form works out itself for any the visitor does not enter)") if needed else " (the server assigns `id`)"
        if getattr(ent, "created_on_opening", False):
            # The first record is the client's to make: the page asks for the record it works on and is given it
            lines.append(
                f"- `src/api/{_to_snake_case(n)}Client.ts` ({role}) exports exactly: `{n}State` (the type of one record), "
                f"`open{n}(): Promise<{n}State>` (the record the page works on: the newest one, or a new one in its "
                f"starting state when none exists; the page calls it once when the page opens and shows what it returns, "
                f"so the page never lists or creates a `{n}` itself to get going), `list{n}(): Promise<{n}State[]>`, "
                f"`get{n}(id: string)`, `create{n}(data: Partial<{n}State>)` (the server assigns `id`){sending}.")
            continue
        lines.append(f"- `src/api/{_to_snake_case(n)}Client.ts` ({role}) exports exactly: `{n}State` (the type of one record), "
                     f"`list{n}(): Promise<{n}State[]>`, `get{n}(id: string)`, `create{n}(data: Partial<{n}State>)`{create_note}{sending}.")
    return "\n".join(lines)


def synthesize_and_write_presentation_projection(
    pitch: str,
    structure: DomainStructureSchema,
    inbox_specs: List[BusinessSpec],
    workspace_dir: str,
    action_manifest: Optional[Dict[str, Any]] = None,
    router_code: Optional[str] = None,
    ux_blueprint: Optional[str] = None,
    intent: Optional[ProductIntent] = None
) -> Dict[str, Any]:
    """
    Directly synthesizes and writes modular React presentation components and client.
    Guarantees Anti-Monolith Invariant (App.tsx < 100 LOC, components < 150 LOC)
    and strictly enforces zero contract drift with the backend Action Protocol.
    """
    start_time = time.time()
    domain_name = _sanitize_name(structure.domain_name or "Application")

    master_entity = structure.master_entity()

    master_name = _sanitize_name(master_entity.name) if master_entity else domain_name
    master_slug = _to_snake_case(master_name)

    entity_summaries = []
    for ent in structure.entities:
        attr_desc = ", ".join(a.describe() for a in ent.attributes)
        role = f", {ent.audience_role.value.replace('_', ' ')}" if ent.audience_role.value != "internal" else ""
        entity_summaries.append(f"- **{ent.name}** ({'Aggregate Root' if ent.is_aggregate_root else 'Entity'}{role}): [{attr_desc}]")
    entities_block = "\n".join(entity_summaries) if entity_summaries else f"- **{master_name}**: Primary Aggregate Root"

    bdd_lines = []
    for idx, spec in enumerate(inbox_specs, 1):
        bdd_lines.append(f"- **Invariant {idx} [{spec.title}]** ({spec.target_aggregate}):\n  - {spec.given_when_then}")
    bdd_section = "\n".join(bdd_lines) if bdd_lines else "- Enforce domain validation invariants and valid state progression."

    provable_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    rel_ws = os.path.relpath(workspace_dir, provable_root).replace("\\", "/")

    # Authoritative Action Protocol block (UI actions vs API-only actions)
    action_protocol_block = format_action_protocol(action_manifest)

    # Load prompt template
    prompt_path = os.path.join(os.path.dirname(__file__), "..", "prompts", "presentation_projection_synthesis.md")
    if not os.path.exists(prompt_path):
        prompt_template = """You are Provable's Principal Frontend Architect.
Build the interactive presentation projection for:
## Domain Specification
- **Product Pitch**: "{pitch}"
- **Domain Identity**: `{domain_name}`
- **Master Aggregate**: `{master_name}`
Entities:
{entities_block}
Behavioral Invariants:
{bdd_section}
## Action Protocol:
{action_protocol_block}
Answer with four blocks, each introduced by its marker alone on a line:
<<<view_tsx>>>  complete code for src/views/{master_name}View.tsx
<<<controls_tsx>>>  complete code for src/components/Controls/{master_name}Controls.tsx
<<<history_tsx>>>  complete code for src/components/History/{master_name}History.tsx
<<<app_tsx>>>  complete code for src/App.tsx under 100 LOC
"""
    else:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()

    # The authoritative backend model: the dataclass of the master and of every other entity the audience creates
    # (owned by the skeleton and the TDD loop), read now so the page sees the fields they really have. In a
    # kickstart the methods are being written at the same time; what the page needs of them is in the manifest.
    created = [_sanitize_name(e.name) for e in structure.entities
               if getattr(e.audience_role, "value", None) == "created_by_audience" and _sanitize_name(e.name) != master_name]
    class_sources = []
    for class_name in [master_name] + created:
        domain_path = os.path.join(workspace_dir, "src", "domain", f"{_to_snake_case(class_name)}.py")
        if os.path.exists(domain_path):
            with open(domain_path, "r", encoding="utf-8") as f:
                source = f.read().strip()
            class_sources.append(source[source.index("@dataclass"):] if class_sources and "@dataclass" in source else source)
    backend_state_model = "\n\n\n".join(class_sources)
    if not backend_state_model:
        backend_state_model = f"# (domain module for {master_name} not written yet)"

    if ux_blueprint is None:
        try:
            from onboarding.ux_planner import plan_ux_blueprint
            ux_blueprint = plan_ux_blueprint(
                pitch=pitch,
                structure=structure,
                action_manifest=action_manifest,
                backend_state_model=backend_state_model,
                master_name=master_name,
                master_slug=master_slug,
                intent=intent
            )
        except Exception as ux_err:
            print(f"[Compiler:Node3] UX planning notice: {ux_err}")
            ux_blueprint = "Default user intake and primary domain actions."

    prompt = prompt_template
    replacements = {
        "{pitch}": pitch,
        "{domain_name}": domain_name,
        "{master_name}": master_name,
        "{master_slug}": master_slug,
        "{master_plural}": _pluralize(master_slug),   # the route the skeleton mounts the router on
        "{rel_workspace}": rel_ws,
        "{entities_block}": entities_block,
        "{clients_block}": _clients_block(structure.presented_entities() or ([master_entity] if master_entity else []), master_name,
                                          actions=(action_manifest or {}).get("actions")),
        "{gestures_block}": page_gestures.gestures_block(),
        "{opening_block}": page_opening.opening_block(),
        "{bdd_section}": bdd_section,
        "{backend_state_model}": backend_state_model,
        "{action_protocol_block}": action_protocol_block,
        "{ux_blueprint}": ux_blueprint or "",
        "{intent_block}": intent_block(intent),
        "{page_parts}": parts_block(ux_blueprint or ""),
    }
    for k, v in replacements.items():
        prompt = prompt.replace(k, str(v))

    print(f"[Compiler:Node3] Synthesizing interactive presentation projection and modular UI...", flush=True)

    raw_response = call_gemini(prompt, stage="presentation_projection_synthesis", timeout_s=PAGE_TIMEOUT_S)
    created_files = []

    if not raw_response:
        reason = agent_orchestrator.LAST_LLM_ERROR or "the LLM returned an empty response"
        print(f"[Compiler:Node3] ⚠️ No presentation projection: {reason}", flush=True)
        return {"success": False, "error": reason, "files": [], "elapsed_seconds": round(time.time() - start_time, 2)}

    try:
        payload = parse_file_blocks(raw_response)
    except ValueError as e:
        reason = f"the answer is not the four marked file blocks: {e}"
        print(f"[Compiler:Node3] ⚠️ Failed to read the presentation projection: {reason}", flush=True)
        return {"success": False, "error": reason, "files": [], "elapsed_seconds": round(time.time() - start_time, 2)}

    # Target directories (write to both workspace/src and workspace/frontend/src if present)
    target_roots = [os.path.join(workspace_dir, "src")]
    frontend_src = os.path.join(workspace_dir, "frontend", "src")
    if os.path.exists(os.path.join(workspace_dir, "frontend")):
        target_roots.append(frontend_src)

    # The API clients are deterministic (skeleton_builder.generate_master_client, one per presented entity); the model only writes the UI
    from onboarding.skeleton_builder import generate_master_client
    client_files = {f"{_to_snake_case(_sanitize_name(e.name))}Client.ts":
                        generate_master_client(e, actions=(action_manifest or {}).get("actions"))
                    for e in (structure.presented_entities() or ([master_entity] if master_entity else []))}
    client_files[page_gestures.FILE_NAME] = page_gestures.GESTURES_TS
    client_files[page_opening.FILE_NAME] = page_opening.OPENING_TS
    planned = page_parts.parts_of(ux_blueprint or "")
    if planned:  # the role and name of each part of the plan, for the page to spread (page_parts.py)
        client_files[page_parts.FILE_NAME] = page_parts.props_module(planned, page_parts.field_wordings(ux_blueprint))
    omitted = [name for name in SECTIONS if not is_component_file(payload.get(name))]
    view_code = payload.get("view_tsx")
    controls_code = payload.get("controls_tsx") if "controls_tsx" not in omitted else None
    history_code = payload.get("history_tsx") if "history_tsx" not in omitted else None
    app_code = payload.get("app_tsx")

    # No substitute shell: an App that does not wire the master view is a failed generation, reported as such
    if not (app_code and f"{master_name}View" in app_code and "export" in app_code):
        reason = "the answer has no App.tsx that exports an App and imports the master view"
        print(f"[Compiler:Node3] Presentation projection rejected: {reason}", flush=True)
        return {"success": False, "error": reason, "files": [], "elapsed_seconds": round(time.time() - start_time, 2)}

    from onboarding.skeleton_builder import generate_frontend_main_tsx
    resilient_main_tsx = generate_frontend_main_tsx()

    contract_files: List[str] = []  # written from the domain model, not by the model: later repairs leave them alone
    for root in target_roots:
        mapping = {
            os.path.join(root, "views", f"{master_name}View.tsx"): view_code,
            os.path.join(root, "components", "Controls", f"{master_name}Controls.tsx"): controls_code,
            os.path.join(root, "components", "History", f"{master_name}History.tsx"): history_code,
            os.path.join(root, "App.tsx"): app_code,
            os.path.join(root, "main.tsx"): resilient_main_tsx,
        }

        for client_name, client_code in client_files.items():
            mapping[os.path.join(root, "api", client_name)] = client_code
            contract_files.append(os.path.join(root, "api", client_name))

        for path, code in mapping.items():
            if code and code.strip():
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(code.strip() + "\n")
                if path not in created_files:
                    created_files.append(path)

    elapsed = round(time.time() - start_time, 2)
    served_root = target_roots[0]
    component_lines = {
        "src/" + os.path.relpath(path, served_root).replace(os.sep, "/"): len(code.strip().splitlines())
        for path, code in ((os.path.join(served_root, "views", f"{master_name}View.tsx"), view_code),
                           (os.path.join(served_root, "components", "Controls", f"{master_name}Controls.tsx"), controls_code),
                           (os.path.join(served_root, "components", "History", f"{master_name}History.tsx"), history_code),
                           (os.path.join(served_root, "App.tsx"), app_code))
        if code and code.strip()
    }
    print(f"[Compiler:Node3] ✓ Synthesized {len(created_files)} presentation files in {elapsed}s "
          f"(components: {component_lines}; not written: {omitted or 'none'})", flush=True)
    return {
        "success": True,
        "files": created_files,
        "contract_files": contract_files,
        "omitted": omitted,  # the files the model had no component for
        "ux_blueprint": ux_blueprint,
        "component_lines": component_lines,
        "elapsed_seconds": elapsed,
        "master_name": master_name,
        "master_slug": master_slug
    }
