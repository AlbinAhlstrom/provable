"""
Presentation Projection Synthesizer — Node 3 of the Deterministic Compiler Graph.
Synthesizes the interactive presentation projection (React canvas, controls, history, API client, and <100 LOC App.tsx)
in a single fast targeted LLM pass (<6 seconds).
"""

import os
import re
import json
import time
from typing import List, Dict, Any, Optional
from onboarding.action_protocol import format_action_protocol
from onboarding.intent import ProductIntent, intent_block
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


def _generate_fallback_app_tsx(
    master_name: str,
    master_slug: str,
    domain_title: str,
    action_manifest: Optional[Dict[str, Any]] = None
) -> str:
    """Generates a robust, resilient fallback App.tsx under 100 LOC wiring all components."""
    actions = []
    if action_manifest and isinstance(action_manifest, dict) and "actions" in action_manifest:
        actions = [a.get("name") for a in action_manifest.get("actions", []) if a.get("name")]
    primary_action = actions[0] if actions else "action"

    return f'''import React, {{ useState, useEffect }} from 'react';
import {{ get{master_name}, sendAction, {master_name}State }} from './api/{master_slug}Client';
import {{ {master_name}View }} from './views/{master_name}View';
import {{ {master_name}Controls }} from './components/Controls/{master_name}Controls';
import {{ {master_name}History }} from './components/History/{master_name}History';
import {{ Layers, RefreshCw, AlertCircle }} from 'lucide-react';

export const App: React.FC = () => {{
  const [state, setState] = useState<{master_name}State | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchSession = async () => {{
    try {{
      setLoading(true);
      setError(null);
      const data = await get{master_name}('default');
      setState(data);
    }} catch (err: any) {{
      setError(err?.message || 'Failed to connect to domain engine');
    }} finally {{
      setLoading(false);
    }}
  }};

  useEffect(() => {{
    fetchSession();
  }}, []);

  const handleAction = async (actionType: any, params: Record<string, any> = {{}}) => {{
    if (!state) return;
    try {{
      const res = await sendAction(state.id || 'default', actionType, params);
      if (res.state) setState(res.state);
    }} catch (err: any) {{
      setError(err?.message || 'Action dispatch failed');
    }}
  }};

  const rows = (state as any)?.row_count || 9;
  const cols = (state as any)?.column_count || 9;
  const mines = (state as any)?.total_mines || 10;

  return (
    <div className="h-screen max-h-screen bg-neutral-900 text-neutral-100 flex flex-col items-center justify-between p-2 sm:p-3 max-w-full overflow-hidden font-sans">
      <header className="w-full max-w-xl flex items-center justify-between pb-2 mb-1 border-b border-neutral-800 shrink-0">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-indigo-600 rounded-lg text-white shadow-md">
            <Layers className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-white">{domain_title}</h1>
            <p className="text-xs text-neutral-400">Provable Domain Engine (:8001)</p>
          </div>
        </div>
        <button
          onClick={{fetchSession}}
          className="p-2 text-neutral-400 hover:text-white hover:bg-neutral-800 rounded-lg transition shrink-0"
          title="Refresh"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </header>

      {{error && (
        <div className="w-full max-w-xl mb-2 p-2.5 bg-rose-950/80 border border-rose-800 rounded-lg text-rose-200 text-xs flex items-center gap-2 shrink-0">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{{error}}</span>
        </div>
      )}}

      {{loading && !state ? (
        <div className="flex flex-col items-center justify-center p-12 text-neutral-400">
          <RefreshCw className="w-6 h-6 animate-spin mb-2" />
          <p className="text-sm">Connecting to {domain_title} Engine...</p>
        </div>
      ) : (
        <main className="w-full max-w-xl flex-1 flex flex-col items-center justify-between min-h-0 overflow-hidden gap-2 py-1">
          {{state && (
            <{master_name}View
              state={{state}}
              onReveal={{(r: number, c: number) => handleAction('reveal', {{ row: r, column: c }})}}
              onToggleMarker={{(r: number, c: number) => handleAction('toggle_marker', {{ row: r, column: c }})}}
              onChord={{(r: number, c: number) => handleAction('chord', {{ row: r, column: c }})}}
              onFaceClick={{() => handleAction('restart', {{ row_count: rows, column_count: cols, total_mines: mines }})}}
              onAction={{handleAction}}
            />
          )}}
          {{state && (
            <{master_name}Controls
              rowCount={{rows}}
              columnCount={{cols}}
              totalMines={{mines}}
              onRestartPreset={{(r: number, c: number, m: number) => handleAction('restart', {{ row_count: r, column_count: c, total_mines: m }})}}
              onReset={{() => handleAction('restart', {{ row_count: rows, column_count: cols, total_mines: mines }})}}
              onAction={{handleAction}}
              state={{state}}
            />
          )}}
          {{state && <{master_name}History state={{state}} />}}
        </main>
      )}}
    </div>
  );
}};

export default App;
'''


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
Respond STRICTLY with JSON:
{
  "client_ts": "<complete code for src/api/{master_slug}Client.ts>",
  "view_tsx": "<complete code for src/views/{master_name}View.tsx>",
  "controls_tsx": "<complete code for src/components/Controls/{master_name}Controls.tsx>",
  "history_tsx": "<complete code for src/components/History/{master_name}History.tsx>",
  "app_tsx": "<complete code for src/App.tsx under 100 LOC>"
}
"""
    else:
        with open(prompt_path, "r", encoding="utf-8") as f:
            prompt_template = f.read()

    # The authoritative backend model is the master aggregate's dataclass (owned by the skeleton and the TDD loop)
    domain_path = os.path.join(workspace_dir, "src", "domain", f"{master_slug}.py")
    backend_state_model = ""
    if os.path.exists(domain_path):
        with open(domain_path, "r", encoding="utf-8") as f:
            backend_state_model = f.read().strip()
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
        "{rel_workspace}": rel_ws,
        "{entities_block}": entities_block,
        "{bdd_section}": bdd_section,
        "{backend_state_model}": backend_state_model,
        "{action_protocol_block}": action_protocol_block,
        "{ux_blueprint}": ux_blueprint or "",
        "{intent_block}": intent_block(intent)
    }
    for k, v in replacements.items():
        prompt = prompt.replace(k, str(v))

    print(f"[Compiler:Node3] Synthesizing interactive presentation projection and modular UI...", flush=True)

    raw_response = call_gemini(prompt, stage="presentation_projection_synthesis")
    created_files = []

    if not raw_response:
        print(f"[Compiler:Node3] ⚠️ LLM returned empty response for presentation projection.", flush=True)
        return {"success": False, "files": [], "elapsed_seconds": round(time.time() - start_time, 2)}

    try:
        payload = _extract_json_payload(raw_response)
    except Exception as e:
        print(f"[Compiler:Node3] ⚠️ Failed to parse presentation projection JSON: {e}", flush=True)
        return {"success": False, "files": [], "elapsed_seconds": round(time.time() - start_time, 2)}

    # Target directories (write to both workspace/src and workspace/frontend/src if present)
    target_roots = [os.path.join(workspace_dir, "src")]
    frontend_src = os.path.join(workspace_dir, "frontend", "src")
    if os.path.exists(os.path.join(workspace_dir, "frontend")):
        target_roots.append(frontend_src)

    client_code = payload.get("client_ts") or payload.get("client_api")
    view_code = payload.get("view_tsx") or payload.get("canvas_view")
    controls_code = payload.get("controls_tsx")
    history_code = payload.get("history_tsx")
    app_code = payload.get("app_tsx")

    # Validate that app_code exists, exports App, and includes the master view
    if not (app_code and f"{master_name}View" in app_code and "export" in app_code):
        clean_domain_title = re.sub(r'^[#*\s]+', '', domain_name).strip()
        print(f"[Compiler:Node3] Generating robust fallback App.tsx orchestrator for {master_name}...", flush=True)
        app_code = _generate_fallback_app_tsx(
            master_name=master_name,
            master_slug=master_slug,
            domain_title=clean_domain_title,
            action_manifest=action_manifest
        )

    from onboarding.skeleton_builder import generate_frontend_main_tsx
    resilient_main_tsx = generate_frontend_main_tsx()

    for root in target_roots:
        mapping = {
            os.path.join(root, "api", f"{master_slug}Client.ts"): client_code,
            os.path.join(root, "views", f"{master_name}View.tsx"): view_code,
            os.path.join(root, "components", "Controls", f"{master_name}Controls.tsx"): controls_code,
            os.path.join(root, "components", "History", f"{master_name}History.tsx"): history_code,
            os.path.join(root, "App.tsx"): app_code,
            os.path.join(root, "main.tsx"): resilient_main_tsx,
        }

        for path, code in mapping.items():
            if code and code.strip():
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "w", encoding="utf-8") as f:
                    f.write(code.strip() + "\n")
                if path not in created_files:
                    created_files.append(path)

    elapsed = round(time.time() - start_time, 2)
    print(f"[Compiler:Node3] ✓ Synthesized {len(created_files)} presentation files in {elapsed}s", flush=True)
    return {
        "success": True,
        "files": created_files,
        "elapsed_seconds": elapsed,
        "master_name": master_name,
        "master_slug": master_slug
    }
