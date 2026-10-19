"""
Tests after a commit run in the background (.claude/hooks/background_tests.py); only a deploy waits for them.

A commit used to wait for the whole suite (four minutes on one core, a minute in parallel), while `dev` is never
deployed. Now a commit starts the suite on its own checkout and work goes on; a failure is reported at the next
step, and pushing to `main` needs the shipped commit green.
"""
import importlib.util
import json
import os
import subprocess

import pytest

HOOKS = os.path.join(os.path.dirname(__file__), "..", "..", "..", ".claude", "hooks")


def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HOOKS, filename))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def bt():
    return _load("provable_background_tests", "background_tests.py")


@pytest.fixture(scope="module")
def guard():
    return _load("provable_guard_for_bt", "guard.py")


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def repo(tmp_path):
    """A repository with one commit, installed packages beside it, and an uncommitted change on top."""
    root = tmp_path / "repo"
    (root / "frontend").mkdir(parents=True)
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@t")
    _git(root, "config", "user.name", "t")
    (root / ".gitignore").write_text("node_modules/\n/logs/\n", encoding="utf-8")
    (root / "frontend" / "app.ts").write_text("committed", encoding="utf-8")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "one")
    for packages in ("frontend/node_modules", "workspace/node_modules"):
        (root / packages / "vite").mkdir(parents=True)
        (root / packages / "vite" / "keep.txt").write_text("installed", encoding="utf-8")
    (root / "frontend" / "app.ts").write_text("edited after the commit", encoding="utf-8")
    return root


def test_the_suite_runs_on_the_commit_itself_with_the_installed_packages(bt, repo, tmp_path):
    """Verify the result belongs to the commit: work goes on in the tree while the suite runs, so it runs on a
    checkout of the commit, and the installed packages are reached without being copied or touched.

    id: TST-BG-TESTS-001
    Given: A commit, an edit made after it, and installed packages in the tree
    When: The commit's checks run
    Then: They see the committed file and the packages; the result is recorded as passed for that commit, and once
          the checkout is gone the packages and the edit are still there
    """
    sha = _git(repo, "rev-parse", "HEAD")
    seen = {}

    def suite(cwd):
        seen["file"] = (open(os.path.join(cwd, "frontend", "app.ts"), encoding="utf-8").read())
        seen["frontend"] = os.path.exists(os.path.join(cwd, "frontend", "node_modules", "vite", "keep.txt"))
        seen["workspace"] = os.path.exists(os.path.join(cwd, "workspace", "node_modules", "vite", "keep.txt"))
        seen["cwd"] = cwd
        return 0, "12 passed"

    result = bt.run(str(repo), sha, suite=suite, build=lambda cwd: (0, "built"))

    assert seen["file"] == "committed" and seen["frontend"] and seen["workspace"]
    assert result["status"] == "passed" and result["commit"] == sha
    assert bt.read(str(repo), sha)["status"] == "passed"
    assert not os.path.exists(seen["cwd"])
    assert (repo / "frontend" / "node_modules" / "vite" / "keep.txt").read_text(encoding="utf-8") == "installed"
    assert (repo / "workspace" / "node_modules" / "vite" / "keep.txt").exists()
    assert (repo / "frontend" / "app.ts").read_text(encoding="utf-8") == "edited after the commit"
    assert len(_git(repo, "worktree", "list").splitlines()) == 1


def test_the_frontend_is_built_only_for_a_commit_that_changes_it_and_a_failure_keeps_its_output(bt, repo):
    """
    id: TST-BG-TESTS-002
    Given: A commit that changes the frontend, and a build that fails
    When: Its checks run
    Then: The build ran, the result is failed and holds the build's output
    """
    sha = _git(repo, "rev-parse", "HEAD")
    built = []

    result = bt.run(str(repo), sha, suite=lambda cwd: (0, ""), build=lambda cwd: built.append(cwd) or (2, "TS2304"))

    assert built and result["status"] == "failed" and "TS2304" in result["output"]


def test_a_commit_starts_its_checks_once_and_other_commands_start_nothing(bt, repo):
    """Verify the commit is not held up: the hook after a command starts the checks of a new commit and returns.

    id: TST-BG-TESTS-003
    Given: The hook after a tool call
    When: A command that committed runs, the same commit is seen again, and a command that did not commit runs
    Then: The checks of that commit were started once, marked running
    """
    sha = _git(repo, "rev-parse", "HEAD")
    started = []

    def start(root, commit):
        started.append(commit)
        bt.write(root, {"commit": commit, "status": "running"})

    for command in ('git add -- a.py && git commit -q -m "x"', "git commit --amend --no-edit", "ls"):
        bt.after_tool({"tool_name": "Bash", "tool_input": {"command": command}}, str(repo), start=start)

    assert started == [sha]
    assert bt.read(str(repo), sha)["status"] == "running"


def test_a_failure_is_reported_at_the_next_step_once(bt, repo):
    """
    id: TST-BG-TESTS-004
    Given: Checks of a commit that failed
    When: Two tool calls follow
    Then: The first is told which commit failed and what failed; the second is told nothing
    """
    bt.write(str(repo), {"commit": "abc1234def", "status": "failed", "output": "FAILED test_x.py::test_y"})

    first = bt.after_tool({"tool_name": "Read", "tool_input": {}}, str(repo), start=lambda root, commit: None)
    second = bt.after_tool({"tool_name": "Read", "tool_input": {}}, str(repo), start=lambda root, commit: None)

    assert "abc1234" in first and "test_x.py::test_y" in first
    assert second == ""


@pytest.mark.parametrize("command, shipped", [
    ("git push origin origin/dev:main", "origin/dev"),
    ("git push origin HEAD:main", "HEAD"),
    ("git push origin main", "main"),
    ("git push -q origin dev", None),
    ("git push origin dev:dev", None),
    ("git log origin/dev:main", None),
])
def test_a_deploy_is_recognised_by_what_it_pushes_to_main(guard, command, shipped):
    """
    id: TST-BG-TESTS-005
    Given: Push commands
    When: The guard reads them
    Then: A push to main names what it ships; any other command is no deploy
    """
    assert guard.deploy_source(command) == shipped


def test_a_deploy_ships_only_a_commit_whose_checks_passed(guard, bt, repo):
    """Verify the one gate left: what goes to main has passed the suite, waited for when it is still running and run
    when it never was.

    id: TST-BG-TESTS-006
    Given: A commit whose checks passed, failed, are still running, or never ran
    When: It is deployed
    Then: Passed ships; failed is refused with what failed; running is waited for; never run is run first
    """
    sha = _git(repo, "rev-parse", "HEAD")

    def verdict(result, ran=None):
        if result is not None:
            bt.write(str(repo), {"commit": sha, **result})
        else:
            path = bt.result_path(str(repo), sha)
            if os.path.exists(path):
                os.remove(path)
        return guard.deploy_gate(str(repo), sha, bt,
                                 run=lambda root, commit: ran.append(commit) or {"commit": commit, "status": "passed"},
                                 wait=lambda root, commit: {"commit": commit, "status": "failed", "output": "late"})

    assert verdict({"status": "passed"}) is None
    assert "boom" in verdict({"status": "failed", "output": "boom"})
    assert "late" in verdict({"status": "running"})
    ran = []
    assert verdict(None, ran) is None and ran == [sha]


def test_a_commit_no_longer_waits_for_the_suite(guard, monkeypatch):
    """
    id: TST-BG-TESTS-007
    Given: The guard before a tool call
    When: A commit command comes in
    Then: No suite and no build is run before it
    """
    monkeypatch.setattr(guard.subprocess, "run", lambda *a, **k: pytest.fail(f"ran before the commit: {a}"))
    assert guard.before_tool({"tool_name": "Bash", "tool_input": {"command": 'git commit -m "x"'}}, "/repo") is None


def test_the_build_runs_only_when_the_commit_changes_the_frontend(bt):
    calls = []

    def runner(label):
        def run():
            calls.append(label)
            return 0, ""
        return run

    bt.checks(changed=["backend/app.py"], suite=runner("tests"), build=runner("build"))
    assert calls == ["tests"]

    calls.clear()
    bt.checks(changed=["frontend/src/App.tsx"], suite=runner("tests"), build=runner("build"))
    assert calls == ["tests", "build"]


def test_the_checks_report_the_first_failure(bt):
    message = bt.checks(
        changed=["frontend/src/App.tsx"],
        suite=lambda: (1, "2 failed"),
        build=lambda: (0, ""),
    )
    assert "2 failed" in message

    message = bt.checks(
        changed=["frontend/src/App.tsx"],
        suite=lambda: (0, ""),
        build=lambda: (2, "TS2304"),
    )
    assert "TS2304" in message
    assert bt.checks(changed=[], suite=lambda: (0, ""), build=lambda: (0, "")) is None


def test_the_checks_start_without_a_window_of_their_own(bt, repo, monkeypatch):
    """Verify the checks stay out of sight on Windows: started with no console at all, every program they start
    (the suite's workers) opened a console window of its own; with a hidden console they share it.

    id: TST-BG-TESTS-008
    Given: A commit's checks being started on Windows
    When: The process is started
    Then: It gets a hidden console of its own, not none, in a group of its own
    """
    sha, started = _git(repo, "rev-parse", "HEAD"), {}
    monkeypatch.setattr(bt.os, "name", "nt")
    for flag, value in (("CREATE_NO_WINDOW", 0x08000000), ("DETACHED_PROCESS", 0x8), ("CREATE_NEW_PROCESS_GROUP", 0x200)):
        monkeypatch.setattr(bt.subprocess, flag, value, raising=False)
    monkeypatch.setattr(bt.subprocess, "Popen", lambda *a, **k: started.update(k))

    bt.start(str(repo), sha)

    flags = started["creationflags"]
    assert flags & 0x08000000 and flags & 0x200 and not flags & 0x8
