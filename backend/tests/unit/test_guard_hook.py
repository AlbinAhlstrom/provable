"""
The PreToolUse guard (.claude/hooks/guard.py) enforces the workspace airgap and the launcher rule.

`static_violation` is the pure decision; the commit gate (full suite, frontend build) is exercised by
`commit_gates` with injected runners so no subprocess is started here.
"""
import importlib.util
import os

import pytest

GUARD_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "hooks", "guard.py")
ROOT = "/repo"


@pytest.fixture(scope="module")
def guard():
    spec = importlib.util.spec_from_file_location("provable_guard", GUARD_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def bash(guard, command):
    return guard.static_violation("Bash", {"command": command}, ROOT)


@pytest.mark.parametrize("path", ["/repo/workspace/src/app.py", "/repo/workspace/frontend/App.tsx"])
def test_edit_and_write_inside_workspace_are_blocked(guard, path):
    for tool in ("Edit", "Write"):
        assert guard.static_violation(tool, {"file_path": path}, ROOT)


def test_edit_outside_workspace_is_allowed(guard):
    assert not guard.static_violation("Edit", {"file_path": "/repo/backend/app.py"}, ROOT)
    assert not guard.static_violation("Edit", {"file_path": "/repo/workspace_notes.md"}, ROOT)


@pytest.mark.parametrize("command", [
    "echo x > workspace/src/app.py",
    "echo x >> ./workspace/notes.txt",
    "cat a | tee workspace/src/a.py",
    "sed -i 's/a/b/' workspace/src/app.py",
    "rm -rf workspace/src",
    "mv a.py workspace/src/a.py",
    "cd workspace && git add -A",
    "git -C workspace commit -m x",
    "git -C workspace reset --hard",
])
def test_shell_writes_into_workspace_are_blocked(guard, command):
    assert bash(guard, command), command


@pytest.mark.parametrize("command", [
    "ls workspace/src",
    "cat workspace/src/app.py",
    "grep -rn Order workspace/src > logs/out.txt",
    "git -C workspace log --oneline",
    "git -C workspace status",
    "git -C workspace diff",
    "cp workspace/src/app.py logs/app_copy.py",
])
def test_shell_reads_of_workspace_are_allowed(guard, command):
    assert not bash(guard, command), command


@pytest.mark.parametrize("command", ["python run.py", "python3 ./run.py --x", "cd /repo && python run.py"])
def test_launching_the_stack_by_hand_is_blocked(guard, command):
    assert bash(guard, command)


def test_launcher_allowed_with_explicit_override(guard):
    assert not bash(guard, "PROVABLE_ALLOW_RUN=1 python run.py")


def test_text_mentioning_the_launcher_is_not_a_launch(guard):
    assert not bash(guard, "echo 'never use python run.py by hand' > notes.txt")
    assert not bash(guard, "grep -n 'python run.py' CLAUDE.md")


def test_commit_gate_runs_frontend_build_only_when_frontend_is_staged(guard):
    calls = []

    def runner(label):
        def run():
            calls.append(label)
            return 0, ""
        return run

    guard.commit_gates(staged=["backend/app.py"], backend_tests=runner("tests"), frontend_build=runner("build"))
    assert calls == ["tests"]

    calls.clear()
    guard.commit_gates(staged=["frontend/src/App.tsx"], backend_tests=runner("tests"), frontend_build=runner("build"))
    assert calls == ["tests", "build"]


def test_commit_gate_reports_the_first_failure(guard):
    message = guard.commit_gates(
        staged=["frontend/src/App.tsx"],
        backend_tests=lambda: (1, "2 failed"),
        frontend_build=lambda: (0, ""),
    )
    assert "2 failed" in message

    message = guard.commit_gates(
        staged=["frontend/src/App.tsx"],
        backend_tests=lambda: (0, ""),
        frontend_build=lambda: (2, "TS2304"),
    )
    assert "TS2304" in message
    assert guard.commit_gates(staged=[], backend_tests=lambda: (0, ""), frontend_build=lambda: (0, "")) is None
