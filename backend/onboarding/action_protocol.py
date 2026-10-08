"""Renders the action manifest for the UI-facing stages (UX planning and presentation) and checks it against the code.

The interface serves the product's audience only. Actions performed by anyone else (for example staff
handling what the audience submitted) stay reachable through the API but must get no controls in the UI.
"""

import ast
import os
import re
from typing import Any, Dict, Optional


def _line(act: Dict[str, Any], with_client: bool = False) -> str:
    params = ", ".join(f"`{p}`" for p in act.get("params", [])) or "None"
    desc = f" — {act['description']}" if act.get("description") else ""
    owner = ""
    if with_client and act.get("aggregate"):
        from onboarding.skeleton_builder import to_snake_case
        owner = (f" on `{act['aggregate']}` (`sendAction` of `src/api/{to_snake_case(str(act['aggregate']))}Client.ts`, "
                 f"with the id of that {act['aggregate']})")
    return f"- Action `{act.get('name', 'action')}`{owner}: params [{params}]{desc}"


def format_action_protocol(manifest: Optional[Dict[str, Any]]) -> str:
    if not manifest or not isinstance(manifest.get("actions"), list):
        return "- (No action protocol available: build the read-only views and the creation form only.)"
    ui = [a for a in manifest["actions"] if a.get("performed_by", "audience") != "other"]
    api_only = [a for a in manifest["actions"] if a.get("performed_by") == "other"]
    lines = [_line(a, with_client=True) for a in ui] or ["- (No audience-facing actions.)"]
    if api_only:
        lines.append("")
        lines.append("API-only actions (performed by someone other than this product's audience; render NO buttons, forms, "
                     "labels or copy for them anywhere in the UI):")
        lines.extend(_line(a) for a in api_only)
    return "\n".join(lines)


def format_interface_contract(manifest: Optional[Dict[str, Any]], aggregate: str) -> str:
    """The methods the interface has been told an aggregate offers, for the test/code stages that write them. The
    action protocol is fixed before the specs run, so the TDD loop must give the methods these names, not its own."""
    lines = [_line(a) for a in ((manifest or {}).get("actions") or [])
             if isinstance(a, dict) and a.get("name") and a.get("aggregate") == aggregate]
    return "\n".join(lines) or "(none: no interface method has been promised for this class)"


def check_action_contract(workspace_dir: str, manifest: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Compares the action protocol with the domain code that now exists.

    The manifest is designed before the specs run, and the TDD loop writes the methods afterwards, so the two can
    disagree. A manifest action with no public method on its aggregate answers 404 when the interface calls it.
    Returns {"ok": bool, "implemented": [...], "missing": [{"action", "aggregate", "performed_by"}]}; pure inspection.
    """
    from onboarding.skeleton_builder import to_snake_case

    actions = [a for a in ((manifest or {}).get("actions") or []) if isinstance(a, dict) and a.get("name")]
    methods_by_file: Dict[str, set] = {}

    def methods_of(aggregate: str) -> set:
        path = os.path.join(workspace_dir, "src", "domain", f"{to_snake_case(aggregate)}.py")
        if path not in methods_by_file:
            found: set = set()
            if os.path.exists(path):
                with open(path, "r", encoding="utf-8") as f:
                    tree = ast.parse(f.read())
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef) and node.name == aggregate:
                        found = {n.name for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                                 and not n.name.startswith("_") and n.name != "to_dict"}
            methods_by_file[path] = found
        return methods_by_file[path]

    implemented, missing = [], []
    for action in actions:
        aggregate = action.get("aggregate") or ""
        name = re.sub(r"[^a-z0-9]+", "_", str(action["name"]).strip().lower()).strip("_")  # same normalisation as the router
        (implemented if name in methods_of(aggregate) else missing).append(
            action["name"] if name in methods_of(aggregate) else
            {"action": action["name"], "aggregate": aggregate, "performed_by": action.get("performed_by", "audience")})
    return {"ok": not missing, "implemented": implemented, "missing": missing}
