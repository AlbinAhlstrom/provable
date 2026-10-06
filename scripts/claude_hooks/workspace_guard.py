#!/usr/bin/env python3
"""
PreToolUse guard for the Provable airgap.

`workspace/` is written only by the Provable pipeline (backend/onboarding/,
backend/service_layer/). Any tool call made by an agent that would create,
modify, delete or commit something inside `workspace/` is denied, and the whole
run is halted so the user is notified immediately.

Reading `workspace/` stays allowed: it is the meta-codebase used to compare the
generated output against the expected result.

Covered tools
  - Edit / Write / MultiEdit / NotebookEdit      (exact path check)
  - mcp__remote-devices__device_commit_files     (exact path check)
  - Bash / mcp__remote-devices__device_bash      (heuristic: command text)

The engine itself (run.py -> uvicorn) is a separate process and is not mediated
by hooks, so pipeline writes are unaffected.

Standard library only. Internal errors exit 1 (non-blocking, visible to the user).
"""
import json
import os
import re
import sys

PATH_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
BASH_TOOLS = {"Bash", "mcp__remote-devices__device_bash"}
COMMIT_TOOLS = {"mcp__remote-devices__device_commit_files"}

WORKSPACE_WORD = re.compile(r"(?:^|[\s\"'=/\\])workspace(?:[\s\"'/\\]|$)", re.IGNORECASE)
WRITE_VERBS = re.compile(
    r"(?:^|[\s;&|(])"
    r"(?:rm|rmdir|mv|cp|touch|mkdir|tee|truncate|chmod|ln|del|erase|rd|ren|move|copy|"
    r"xcopy|robocopy|Remove-Item|Move-Item|Copy-Item|New-Item|Set-Content|Add-Content|Out-File|"
    r"Rename-Item|Clear-Content)"
    r"(?=[\s;&|)]|$)",
    re.IGNORECASE,
)
INPLACE_EDIT = re.compile(r"\b(?:sed|perl|awk)\b[^|;&]*\s-[a-zA-Z]*i", re.IGNORECASE)
GIT_MUTATION = re.compile(
    r"\bgit\b[^|;&]*\b(?:add|commit|revert|reset|checkout|restore|clean|stash|apply|rm|mv|"
    r"merge|rebase|cherry-pick|pull|push)\b",
    re.IGNORECASE,
)
PKG_MUTATION = re.compile(
    r"\b(?:npm|pnpm|yarn)\b[^|;&]*\b(?:install|i|add|ci|uninstall|remove|update|upgrade)\b",
    re.IGNORECASE,
)
REDIRECT_TO_WORKSPACE = re.compile(r">>?\s*[^&|;<>]*workspace", re.IGNORECASE)
SCRIPT_WRITE = re.compile(
    r"(?:write_text|write_bytes|shutil\.(?:copy|move|rmtree)|os\.(?:remove|unlink|rename)|"
    r"open\([^)]*[\"'][wax]\+?b?[\"'])",
    re.IGNORECASE,
)


def _norm(path: str) -> str:
    return os.path.normcase(os.path.normpath(path))


def _is_inside(path: str, ws_root: str, cwd: str) -> bool:
    if not path:
        return False
    expanded = os.path.expanduser(path)
    if not os.path.isabs(expanded):
        expanded = os.path.join(cwd, expanded)
    target = _norm(expanded)
    return target == ws_root or target.startswith(ws_root + os.sep)


def _bash_touches_workspace(command: str, cwd_in_workspace: bool) -> str:
    """Return a reason string if the command looks like it writes into workspace/."""
    if not command:
        return ""
    if not (cwd_in_workspace or WORKSPACE_WORD.search(command)):
        return ""
    if REDIRECT_TO_WORKSPACE.search(command):
        return "shell redirection into workspace/"
    if INPLACE_EDIT.search(command):
        return "in-place edit (sed/perl/awk -i)"
    if GIT_MUTATION.search(command):
        return "git command that mutates the tree or history"
    if PKG_MUTATION.search(command):
        return "package manager command that mutates package.json / node_modules / lockfile"
    if WRITE_VERBS.search(command):
        return "file-mutating command"
    if SCRIPT_WRITE.search(command):
        return "inline script that writes files"
    return ""


def _deny(reason: str) -> None:
    message = (
        "AIRGAP VIOLATION BLOCKED: " + reason + ". "
        "workspace/ is written only by the Provable pipeline. "
        "Fix the generator (backend/onboarding/, backend/service_layer/, backend/prompts/) "
        "instead, then regenerate. Reading workspace/ is allowed."
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": message,
        },
        "continue": False,
        "stopReason": message,
    }))
    sys.exit(0)


def main() -> None:
    raw = sys.stdin.read()
    if not raw.strip():
        return
    payload = json.loads(raw)

    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or os.getcwd()
    root = os.environ.get("CLAUDE_PROJECT_DIR") or cwd
    ws_root = _norm(os.path.join(root, "workspace"))

    if tool in PATH_TOOLS:
        path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
        if _is_inside(path, ws_root, cwd):
            _deny(f"{tool} targets {path}")

    elif tool in COMMIT_TOOLS:
        for entry in tool_input.get("files") or []:
            dev_path = (entry or {}).get("devicePath", "")
            if _is_inside(dev_path, ws_root, cwd):
                _deny(f"{tool} writes {dev_path}")

    elif tool in BASH_TOOLS:
        command = tool_input.get("command", "")
        reason = _bash_touches_workspace(command, _is_inside(cwd, ws_root, cwd))
        if reason:
            _deny(f"{reason}: {command[:160]}")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:  # fail visible, never silently open
        print(f"workspace_guard internal error: {exc}", file=sys.stderr)
        sys.exit(1)
