"""Renders the action manifest for the UI-facing stages (UX planning and presentation).

The interface serves the product's audience only. Actions performed by anyone else (for example staff
handling what the audience submitted) stay reachable through the API but must get no controls in the UI.
"""

from typing import Any, Dict, Optional


def _line(act: Dict[str, Any]) -> str:
    params = ", ".join(f"`{p}`" for p in act.get("params", [])) or "None"
    desc = f" — {act['description']}" if act.get("description") else ""
    return f"- Action `{act.get('name', 'action')}`: params [{params}]{desc}"


def format_action_protocol(manifest: Optional[Dict[str, Any]]) -> str:
    if not manifest or not isinstance(manifest.get("actions"), list):
        return "- (No action protocol available: build the read-only views and the creation form only.)"
    ui = [a for a in manifest["actions"] if a.get("performed_by", "audience") != "other"]
    api_only = [a for a in manifest["actions"] if a.get("performed_by") == "other"]
    lines = [_line(a) for a in ui] or ["- (No audience-facing actions.)"]
    if api_only:
        lines.append("")
        lines.append("API-only actions (performed by someone other than this product's audience; render NO buttons, forms, "
                     "labels or copy for them anywhere in the UI):")
        lines.extend(_line(a) for a in api_only)
    return "\n".join(lines)
