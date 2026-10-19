#!/usr/bin/env python3
"""The checks of a commit, run in the background after it is made; only a deploy waits for them (guard.py).

A commit used to wait for the whole backend suite before it was made, while `dev` is never deployed. Now:

- After a tool call that committed (`after-tool`, a PostToolUse hook), the new commit's checks start in a process of
  their own and the call returns: the backend suite in parallel, and the frontend build when the commit changes
  `frontend/`.
- They run on a checkout of the commit (`git worktree`), so what is edited meanwhile is not what is judged. The
  installed packages (`frontend/node_modules`, `workspace/node_modules`) are linked in, never copied; the links are
  removed before the checkout is, so removing it never reaches them.
- The result is kept in `logs/tests/<commit>.json`. A failure is told to the agent at its next tool call, once.
- Pushing to `main` (a deploy) needs the shipped commit passed: guard.py waits for checks still running and runs those
  that never ran.
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time

WAIT_LIMIT_S = 900.0   # checks still "running" after this never finished (their process died)
_PACKAGES = ("frontend/node_modules", "workspace/node_modules")


def result_path(root, commit):
    return os.path.join(root, "logs", "tests", f"{commit}.json")


def read(root, commit):
    try:
        with open(result_path(root, commit), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return None


def write(root, result):
    path = result_path(root, result["commit"])
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    os.replace(path + ".tmp", path)


def _git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)


def checks(changed, suite, build):
    """Runs the suite, and the build when `frontend/` changed. Runners return (exit_code, output). Returns the
    failure's message, or None."""
    code, out = suite()
    if code != 0:
        return "The backend suite failed:\n" + out
    if any(path.startswith("frontend/") for path in changed):
        code, out = build()
        if code != 0:
            return "The frontend build (npm run build) failed:\n" + out
    return None


def _suite(cwd):
    res = subprocess.run([sys.executable, "-m", "pytest", "backend/tests/", "-q", "-n", "auto", "--dist", "worksteal",
                          "-p", "no:cacheprovider"], cwd=cwd, capture_output=True, text=True)
    return res.returncode, res.stdout[-3000:] + res.stderr[-1000:]


def _build(cwd):
    npm = shutil.which("npm") or "npm"
    res = subprocess.run([npm, "run", "build"], cwd=os.path.join(cwd, "frontend"), capture_output=True, text=True)
    return res.returncode, res.stdout[-3000:] + res.stderr[-1000:]


def _link(target, link):
    os.makedirs(os.path.dirname(link), exist_ok=True)
    try:
        os.symlink(target, link, target_is_directory=True)
    except OSError:  # Windows without the symlink privilege: a directory junction needs none
        import _winapi
        _winapi.CreateJunction(target, link)


def _unlink(link):
    """Removes a link and only the link; says whether it is gone."""
    for remove in (os.unlink, os.rmdir):
        try:
            remove(link)
        except OSError:
            continue
        break
    return not os.path.lexists(link)


def run(root, commit, suite=_suite, build=_build):
    """Runs the checks of `commit` on a checkout of it, records the result and returns it."""
    started = time.time()
    write(root, {"commit": commit, "status": "running", "pid": os.getpid(), "started_at": started})
    checkout = os.path.join(tempfile.gettempdir(), "provable-checks", f"{commit[:12]}-{os.getpid()}")
    added = _git(root, "worktree", "add", "--detach", checkout, commit)
    if added.returncode != 0:
        result = {"commit": commit, "status": "failed", "output": "No checkout of the commit: " + added.stderr}
        write(root, result)
        return result
    links = []
    try:
        for packages in _PACKAGES:
            if os.path.isdir(os.path.join(root, packages)):
                links.append(os.path.join(checkout, packages))
                _link(os.path.join(root, packages), links[-1])
        changed = _git(root, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", commit).stdout.split()
        failure = checks(changed, lambda: suite(checkout), lambda: build(checkout))
    except Exception as err:  # the checks could not run: a failure with its reason, never a pass
        failure = f"The checks could not run: {type(err).__name__}: {err}"
    finally:
        left = [link for link in links if not _unlink(link)]
        if left:  # removing the checkout would reach into the installed packages: leave it, and say so
            failure = (failure or "") + f"\nThe checkout {checkout} was left in place: links not removed: {left}"
        else:
            _git(root, "worktree", "remove", "--force", checkout)
            _git(root, "worktree", "prune")
    result = {"commit": commit, "status": "failed" if failure else "passed", "output": failure or "",
              "started_at": started, "finished_at": time.time(), "duration_s": round(time.time() - started, 1)}
    write(root, result)
    return result


def start(root, commit):
    """Starts the checks of `commit` in a process of their own and returns at once."""
    write(root, {"commit": commit, "status": "running", "started_at": time.time()})
    log = os.path.join(root, "logs", "tests", f"{commit}.log")
    options = ({"creationflags": subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP}
               if os.name == "nt" else {"start_new_session": True})
    with open(log, "w", encoding="utf-8") as out:
        subprocess.Popen([sys.executable, os.path.abspath(__file__), "run", root, commit], cwd=root,
                         stdout=out, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, **options)


def wait(root, commit):
    """The result of checks that are running, once they finish."""
    started = time.time()
    while time.time() - started < WAIT_LIMIT_S:
        result = read(root, commit)
        if result is None or result.get("status") != "running":
            return result
        time.sleep(2)
    return {"commit": commit, "status": "failed",
            "output": f"The checks did not finish within {WAIT_LIMIT_S:.0f} s (see logs/tests/{commit}.log)"}


def _unreported_failures(root):
    folder = os.path.join(root, "logs", "tests")
    told = []
    for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
        if not name.endswith(".json"):
            continue
        result = read(root, name[:-len(".json")])
        if result and result.get("status") == "failed" and not result.get("reported"):
            write(root, {**result, "reported": True})
            told.append(f"The checks of commit {result['commit'][:7]} failed; fix it in a new commit:\n"
                        f"{result.get('output', '')[-2500:]}")
    return "\n\n".join(told)


def after_tool(data, root, start=start):
    """After a tool call: starts the checks of a commit it made, and answers what failed since (empty: nothing)."""
    command = (data.get("tool_input") or {}).get("command", "")
    if data.get("tool_name") in ("Bash", "PowerShell") and re.search(r"\bgit\s+commit\b", command):
        head = _git(root, "rev-parse", "HEAD").stdout.strip()
        if head and read(root, head) is None:
            start(root, head)
    return _unreported_failures(root)


def main():
    root = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    if sys.argv[1:2] == ["run"]:
        run(sys.argv[2], sys.argv[3])
        return
    if sys.argv[1:2] == ["after-tool"]:
        data = json.load(sys.stdin)
        told = after_tool(data, root)
        if told:
            print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": told}}))


if __name__ == "__main__":
    main()
