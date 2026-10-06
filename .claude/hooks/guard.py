#!/usr/bin/env python3
"""PreToolUse guard enforcing the invariants from .agents/rules/.

- Blocks edits to workspace/ (generator code in backend/ is the source of truth).
- Blocks `python run.py` (long-lived reloader; the user runs it themselves).
- Runs the full backend test suite before any `git commit`.
Exit code 2 blocks the tool call and feeds stderr back to Claude.
"""
import json
import os
import re
import subprocess
import sys

data = json.load(sys.stdin)
tool = data.get("tool_name")
inp = data.get("tool_input", {})
root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or "."


def block(msg):
    print(msg, file=sys.stderr)
    sys.exit(2)


if tool in ("Edit", "Write"):
    rel = os.path.relpath(os.path.abspath(inp.get("file_path", "")), os.path.abspath(root))
    if rel == "workspace" or rel.startswith("workspace" + os.sep):
        block("workspace/ is off-limits (No Bandages rule). Change the generator in "
              "backend/onboarding/ or backend/prompts/ instead. See .agents/rules/01-architecture-and-meta.md.")

if tool == "Bash":
    cmd = inp.get("command", "")
    if re.search(r"(^|[;&|]\s*)python3?\s+(\./)?run\.py\b", cmd):
        block("Do not run `python run.py` from the agent; the user manages the stack in their own terminal.")
    if re.search(r"\bgit\s+commit\b", cmd):
        res = subprocess.run([sys.executable, "-m", "pytest", "backend/tests/", "-q"],
                             cwd=root, capture_output=True, text=True)
        if res.returncode != 0:
            block("Full test suite must pass before committing:\n" + res.stdout[-3000:] + res.stderr[-1000:])
