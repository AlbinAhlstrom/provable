"""Renders the action manifest for the UI-facing stages (UX planning and presentation) and checks it against the code.

The interface serves the product's audience only. Actions performed by anyone else (for example staff
handling what the audience submitted) stay reachable through the API but must get no controls in the UI. An action
that happens by itself (time passing, a hold running out) is the page's own to send: nothing else runs.
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
        client = f"`src/api/{to_snake_case(str(act['aggregate']))}Client.ts`"
        owner = (f" on `{act['aggregate']}` (`sendKindAction` of {client}: it is done to no one {act['aggregate']}, so "
                 f"it takes no id)" if act.get("on_kind") else
                 f" on `{act['aggregate']}` (`sendAction` of {client}, with the id of that {act['aggregate']})")
    return f"- Action `{act.get('name', 'action')}`{owner}: params [{params}]{desc}"


def format_action_protocol(manifest: Optional[Dict[str, Any]]) -> str:
    if not manifest or not isinstance(manifest.get("actions"), list):
        return "- (No action protocol available: build the read-only views and the creation form only.)"
    ui = [a for a in manifest["actions"] if a.get("performed_by", "audience") not in ("other", "automatic")]
    by_itself = [a for a in manifest["actions"] if a.get("performed_by") == "automatic"]
    api_only = [a for a in manifest["actions"] if a.get("performed_by") == "other"]
    lines = [_line(a, with_client=True) for a in ui] or ["- (No audience-facing actions.)"]
    if by_itself:
        lines.append("")
        lines.append("Actions the page performs by itself (nobody presses anything: the page sends each one when its moment "
                     "comes, as its description says; render no control for them):")
        lines.extend(_line(a, with_client=True) for a in by_itself)
    if api_only:
        lines.append("")
        lines.append("API-only actions (performed by someone other than this product's audience; render NO buttons, forms, "
                     "labels or copy for them anywhere in the UI):")
        lines.extend(_line(a) for a in api_only)
    # The values the page compares against (a status, an outcome), spelled as the domain stores them
    aggregates = list(dict.fromkeys(str(e.get("aggregate")) for e in manifest.get("vocabulary") or [] if isinstance(e, dict)))
    words = [f"{line} (on `{aggregate}`)" for aggregate in aggregates
             for line in shared_words({"vocabulary": manifest.get("vocabulary")}, aggregate)]
    if words:
        lines += ["", "Values the fields hold, exactly as the API returns them:"] + words
    # The page is written while the methods are, so the classes it is shown do not set themselves up yet
    owners = list(dict.fromkeys(str(e.get("aggregate")) for e in manifest.get("starting_states") or [] if isinstance(e, dict)))
    starts = [f"- A newly created `{owner}` holds: {starting_state(manifest, owner)}"
              for owner in owners if starting_state(manifest, owner)]
    if starts:
        lines += ["", "What a record holds when it has just been created, before any action:"] + starts
    return "\n".join(lines)


def starting_state(manifest: Optional[Dict[str, Any]], aggregate: str) -> str:
    """What the manifest says a newly created object of this class holds, "" when it says nothing."""
    for entry in (manifest or {}).get("starting_states") or []:
        if isinstance(entry, dict) and entry.get("aggregate") == aggregate and entry.get("description"):
            return str(entry["description"]).strip()
    return ""


def starts_whole(manifest: Optional[Dict[str, Any]], aggregate: str) -> bool:
    """Whether the manifest says the class's defaults already give a new object its starting state, so the class
    has nothing to write for it (and a test of it would pass on the empty class)."""
    return any(isinstance(entry, dict) and entry.get("aggregate") == aggregate and entry.get("held_by_defaults") is True
               for entry in (manifest or {}).get("starting_states") or [])


def shared_words(manifest: Optional[Dict[str, Any]], aggregate: str) -> list:
    """The words every writer of this class uses alike: the values its fixed-set fields take and the names of its
    refusals, as lines. Tests for a class's rules are written side by side; without these, each invents its own."""
    lines = []
    for entry in (manifest or {}).get("vocabulary") or []:
        if isinstance(entry, dict) and entry.get("aggregate") == aggregate and entry.get("field"):
            values = "; ".join(f'"{v.get("value")}" ({v.get("meaning")})' for v in entry.get("values") or [] if isinstance(v, dict))
            if values:
                lines.append(f"- Field `{entry['field']}` holds exactly one of: {values}")
    for entry in (manifest or {}).get("rejections") or []:
        if isinstance(entry, dict) and entry.get("aggregate") == aggregate and entry.get("error"):
            lines.append(f"- A refusal raises `{entry['error']}` when {entry.get('raised_when') or 'the request is not allowed'}")
    return lines


def actions_in_full(manifest: Optional[Dict[str, Any]], aggregate: str) -> list:
    """What each action of this class does, as the contract wrote it: one line per action that says anything. The
    rules try some of its cases, and the code is written for all of them."""
    return [f"- `{act['name']}({', '.join(str(p) for p in act.get('params') or [])})`: {str(act['description']).strip()}"
            for act in (manifest or {}).get("actions") or []
            if isinstance(act, dict) and act.get("name") and act.get("aggregate") == aggregate
            and str(act.get("description") or "").strip()]


def collection_name(aggregate: str) -> str:
    """The name a kind's stored records go by: the keyword a method is handed them under, and their path in the API."""
    from onboarding.skeleton_builder import _pluralize, to_snake_case
    return _pluralize(to_snake_case(aggregate))


def _handed(act: Dict[str, Any], aggregate: str) -> str:
    """How a method reaches the stored records its action works with, in the words every writer of the class reads.
    The API hands them over by these keywords and stores what the method leaves in them (the generated router)."""
    from onboarding.skeleton_builder import to_snake_case
    given = [str(kind) for kind in act.get("given") or []]
    lists = " and ".join(f"`{collection_name(kind)}` (the list of every stored `{kind}` object)" for kind in given)
    one = (f" It is done to one `{aggregate}`: an ordinary method, called on that record as "
           f"`{to_snake_case(aggregate)}.{act['name']}(...)`.")
    if not given:
        return "" if act.get("on_kind") else one
    if act.get("on_kind"):
        return (f" It is sent to no one `{aggregate}`: it is a `@staticmethod` of `{aggregate}`, called as "
                f"`{aggregate}.{act['name']}(...)`. Besides its params it takes, by keyword, {lists}. These lists are "
                f"the stored records and nothing else is: it reads them, finds in them the record a param names by its "
                f"id, appends a record it makes (with a new `id` from `uuid.uuid4().hex`), removes a record it deletes, "
                f"and returns the `{aggregate}` it made (None when it makes none).")
    return (f"{one} Besides its params it takes, by keyword, {lists}: the stored records and nothing else is, which "
            f"it reads and may change; a record it deletes it removes from its list.")


def format_interface_contract(manifest: Optional[Dict[str, Any]], aggregate: str) -> str:
    """The methods the interface has been told an aggregate offers, for the test/code stages that write them. The
    action protocol is fixed before the specs run, so the TDD loop must give the methods these names, not its own."""
    own = [a for a in ((manifest or {}).get("actions") or [])
           if isinstance(a, dict) and a.get("name") and a.get("aggregate") == aggregate]
    lines = [_line(a) + _handed(a, aggregate) for a in own]
    from onboarding.skeleton_builder import to_snake_case
    others = list(dict.fromkeys(str(kind) for a in own for kind in a.get("given") or [] if kind != aggregate))
    fields = {str(r.get("aggregate")): r.get("fields") or [] for r in (manifest or {}).get("records") or []
              if isinstance(r, dict)}
    for kind in others:  # the other kinds a method is handed: how a test builds one, and what the code reads of it
        built = ", ".join(f"{name}=..." for name in fields.get(kind) or ["id"])
        lines.append(f"- A stored `{kind}` is built as `{kind}({built})`, after `from src.domain.{to_snake_case(kind)} "
                     f"import {kind}`.")
    start = starting_state(manifest, aggregate)
    if start:
        lines.append(f"- A newly created `{aggregate}` (constructed with only its required fields) holds: {start}")
    lines.extend(shared_words(manifest, aggregate))
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
