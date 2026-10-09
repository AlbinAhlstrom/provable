#!/usr/bin/env python3
"""PreToolUse guard enforcing the invariants from .claude/rules/.

- Blocks writes to workspace/ (generator code in backend/ is the source of truth): Edit/Write, and the
  common shell routes (redirects, tee, sed -i, rm/mv/touch/mkdir, git write commands inside it).
- Blocks launching the stack by hand (long-lived reloader; use .claude/hooks/ensure_app_running.sh).
- Runs the full backend test suite before any `git commit`, plus the frontend build when frontend/ is part
  of the commit.
Exit code 2 blocks the tool call and feeds stderr back to Claude.
"""
import json
import os
import re
import shutil
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


def commit_gates(staged, backend_tests, frontend_build):
    """Run the gates a commit must pass. Runners return (exit_code, output). Returns a message or None."""
    code, out = backend_tests()
    if code != 0:
        return "Full test suite must pass before committing:\n" + out
    if any(path.startswith("frontend/") for path in staged):
        code, out = frontend_build()
        if code != 0:
            return "Frontend build (npm run build) must pass before committing frontend changes:\n" + out
    return None


def _git_names(root, *args):
    res = subprocess.run(["git", "diff", "--name-only", *args], cwd=root, capture_output=True, text=True)
    return [line for line in res.stdout.splitlines() if line]


def _staged_for(cmd, root):
    staged = _git_names(root, "--cached")
    if re.search(r"git\s+commit\s+[^|;&]*\s-\w*a\b|git\s+add\b", cmd):
        staged += _git_names(root)  # `commit -a` or an `add` in the same command: not staged yet
    return staged


def _run_backend_tests(root):
    res = subprocess.run([sys.executable, "-m", "pytest", "backend/tests/", "-q"],
                         cwd=root, capture_output=True, text=True)
    return res.returncode, res.stdout[-3000:] + res.stderr[-1000:]


def _run_frontend_build(root):
    npm = shutil.which("npm") or "npm"
    res = subprocess.run([npm, "run", "build"], cwd=os.path.join(root, "frontend"),
                         capture_output=True, text=True)
    return res.returncode, res.stdout[-3000:] + res.stderr[-1000:]


def main():
    data = json.load(sys.stdin)
    tool = data.get("tool_name")
    tool_input = data.get("tool_input", {})
    root = os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or "."

    def block(msg):
        print(msg, file=sys.stderr)
        sys.exit(2)

    reason = static_violation(tool, tool_input, root)
    if reason:
        block(reason)

    cmd = tool_input.get("command", "") if tool == "Bash" else ""
    if re.search(r"\bgit\s+commit\b", cmd):
        message = commit_gates(
            staged=_staged_for(cmd, root),
            backend_tests=lambda: _run_backend_tests(root),
            frontend_build=lambda: _run_frontend_build(root),
        )
        if message:
            block(message)


if __name__ == "__main__":
    main()
