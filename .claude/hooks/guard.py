#!/usr/bin/env python3
"""PreToolUse guard enforcing the invariants from .claude/rules/.

- Blocks writes to workspace/ (generator code in backend/ is the source of truth): Edit/Write, and the
  common shell routes (redirects, tee, sed -i, rm/mv/touch/mkdir, git write commands inside it).
- Blocks launching the stack by hand (long-lived reloader; use .claude/hooks/ensure_app_running.sh).
- Lets a deploy (a push to `main`) through only when the shipped commit's checks passed. A commit itself waits for
  nothing: its checks run in the background after it (background_tests.py).
Exit code 2 blocks the tool call and feeds stderr back to Claude.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys

# "workspace" as a path component: not "myworkspace", ".workspace" or "workspace-inspector.md".
_WS = r"(?<![\w.-])workspace(?:/(?=\S)|(?=[\s\"';&|]|$))"
_WS_PATH = r"(?:\S*/)?workspace/"
_GIT_WRITES = (
    r"(?:add|commit|reset|revert|checkout|clean|rm|mv|restore|push|merge|rebase|stash|apply|cherry-pick|am)"
)

WORKSPACE_WRITE_PATTERNS = [
    re.compile(r">>?\s*[\"']?" + _WS_PATH),
    re.compile(r"\btee\b[^|;&]*" + _WS),
    re.compile(r"\b(?:sed|perl)\b[^|;&]*\s-\w*i\b[^|;&]*" + _WS),
    re.compile(r"\b(?:rm|mv|touch|mkdir|truncate)\b[^|;&]*" + _WS),
    re.compile(r"\bgit\s+-C\s+[\"']?(?:\S*/)?workspace[\"']?\s+" + _GIT_WRITES + r"\b"),
    re.compile(r"\bcd\s+[\"']?(?:\S*/)?workspace[\"']?\s*(?:&&|;)\s*git\s+" + _GIT_WRITES + r"\b"),
]

# `python run.py` only counts when it is the command itself, not text that mentions it.
LAUNCHER = re.compile(r"(?:^|[;&|(\n])\s*(?:\w+=\S+\s+)*python3?\s+(?:\./)?run\.py\b")


def static_violation(tool, tool_input, root):
    """Return the reason a tool call must be blocked, or None. Pure: no subprocess, no I/O."""
    if tool in ("Edit", "Write"):
        rel = os.path.relpath(os.path.abspath(tool_input.get("file_path", "")), os.path.abspath(root))
        if rel == "workspace" or rel.startswith("workspace" + os.sep):
            return ("workspace/ is off-limits (No Bandages rule). Change the generator in "
                    "backend/onboarding/ or backend/prompts/ instead. See .claude/rules/architecture.md.")
    if tool == "Bash":
        cmd = tool_input.get("command", "")
        if any(p.search(cmd) for p in WORKSPACE_WRITE_PATTERNS):
            return ("This command writes to workspace/, which is generated output and off-limits. Change the "
                    "generator in backend/ instead. Reading it is fine. See .claude/rules/architecture.md.")
        if LAUNCHER.search(cmd) and "PROVABLE_ALLOW_RUN=1" not in cmd:
            return ("Do not launch run.py from the agent. Use `bash .claude/hooks/ensure_app_running.sh "
                    "[--restart|--stop]`. If the user explicitly asked for a manual launch, prefix the command "
                    "with PROVABLE_ALLOW_RUN=1 and run it in the background with output to a log file.")
    return None


def deploy_source(cmd):
    """What a push to `main` ships (`origin/dev` in `git push origin origin/dev:main`), or None for any other command."""
    push = re.search(r"\bgit\s+push\b([^|;&\n]*)", cmd)
    if not push:
        return None
    specs = [token for token in push.group(1).split() if not token.startswith("-")][1:]  # the first is the remote
    for spec in specs:
        source, _, target = spec.lstrip("+").rpartition(":")
        if (target or spec).replace("refs/heads/", "") == "main":
            return source or "main"
    return None


def deploy_gate(root, commit, checks, run, wait):
    """Why `commit` may not be deployed, or None. Checks still running are waited for; checks never run are run."""
    result = checks.read(root, commit)
    if result is None:
        result = run(root, commit)
    elif result.get("status") == "running":
        result = wait(root, commit)
    if result and result.get("status") == "passed":
        return None
    return (f"Commit {commit[:7]} is not deployed: its checks did not pass.\n"
            + ((result or {}).get("output") or "no result")[-3000:])


def _background_tests():
    spec = importlib.util.spec_from_file_location(
        "provable_background_tests", os.path.join(os.path.dirname(os.path.abspath(__file__)), "background_tests.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def before_tool(data, root):
    """Why a tool call must be blocked, or None."""
    tool = data.get("tool_name")
    tool_input = data.get("tool_input", {})
    reason = static_violation(tool, tool_input, root)
    if reason:
        return reason
    shipped = deploy_source(tool_input.get("command", "")) if tool in ("Bash", "PowerShell") else None
    if shipped:
        commit = subprocess.run(["git", "rev-parse", shipped], cwd=root, capture_output=True, text=True).stdout.strip()
        if not commit:
            return f"A deploy of {shipped}: no such commit."
        checks = _background_tests()
        return deploy_gate(root, commit, checks, run=checks.run, wait=checks.wait)
    return None


def main():
    data = json.load(sys.stdin)
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or "."
    reason = before_tool(data, root)
    if reason:
        print(reason, file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()
