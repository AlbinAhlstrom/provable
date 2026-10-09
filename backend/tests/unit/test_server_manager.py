"""Dev-server lifecycle: starting the preview must never leave earlier preview servers running."""

import subprocess
import sys
import time

import pytest

from onboarding import server_manager

NETSTAT = """
  Proto  Local Address          Foreign Address        State           PID
  TCP    0.0.0.0:5174           0.0.0.0:0              LISTENING       111
  TCP    [::]:5174              [::]:0                 LISTENING       111
  TCP    127.0.0.1:51740        0.0.0.0:0              LISTENING       222
  TCP    127.0.0.1:5174         127.0.0.1:60000        ESTABLISHED     333
  TCP    0.0.0.0:5175           0.0.0.0:0              LISTENING       444
  TCP    0.0.0.0:5174           0.0.0.0:0              LISTENING       0
"""


def test_listening_pids_matches_the_exact_port_and_only_listeners():
    """Verify only listeners on exactly that port are returned (not 51740, not established clients, not PID 0).

    id: TST-SRV-001
    Given: netstat output with look-alike ports and non-listening rows
    When: The listeners of port 5174 are parsed
    Then: Only PID 111 is returned, once
    """
    assert server_manager._listening_pids(NETSTAT, 5174) == [111]


def _alive(pid: int) -> bool:
    if sys.platform == "win32":
        out = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/NH"], capture_output=True, text=True).stdout
        return str(pid) in out
    try:
        import os
        os.kill(pid, 0)
    except OSError:
        return False
    try:  # a killed process nobody has reaped yet is a zombie: gone, though kill(pid, 0) still finds it
        with open(f"/proc/{pid}/stat") as stat:
            return stat.read().rsplit(")", 1)[1].split()[0] != "Z"
    except (OSError, IndexError):
        return True


def test_terminating_a_server_kills_its_children_not_just_the_shell(tmp_path):
    """Verify the whole process tree dies (npm -> node), which a plain proc.terminate() leaves behind on Windows.

    id: TST-SRV-002
    Given: A shell-like parent that launched a long-running child
    When: The tree is terminated
    Then: Both the parent and the child are gone
    """
    pidfile = tmp_path / "child.pid"
    child = f"import time; open(r'{pidfile}', 'w').write(str(__import__('os').getpid())); time.sleep(120)"
    parent = f"import subprocess, sys, time; subprocess.Popen([sys.executable, '-c', {child!r}]); time.sleep(120)"
    proc = subprocess.Popen([sys.executable, "-c", parent], start_new_session=True)
    for _ in range(50):
        if pidfile.exists() and pidfile.read_text():
            break
        time.sleep(0.1)
    child_pid = int(pidfile.read_text())
    assert _alive(proc.pid) and _alive(child_pid)

    server_manager._terminate_tree(proc)
    time.sleep(1)
    assert not _alive(child_pid) and not _alive(proc.pid)


def test_starting_the_preview_frees_the_port_first_and_launches_once(monkeypatch, tmp_path):
    """Verify a (re)start replaces whatever holds the dev port, so reloads cannot pile up servers.

    id: TST-SRV-003
    Given: A backend that starts again (hot reload) while an earlier preview still holds the port
    When: start_project_servers runs
    Then: The port is freed before the single new launch
    """
    (tmp_path / "package.json").write_text("{}", encoding="utf-8")
    events = []
    monkeypatch.setattr(server_manager, "get_workspace_base", lambda: str(tmp_path))
    monkeypatch.setattr(server_manager, "get_project_settings",
                        lambda: {"dev_server": {"enabled": True, "start_command": "npm run dev", "port": 5174}})
    monkeypatch.setattr(server_manager, "free_port", lambda port: events.append(("free", port)))
    monkeypatch.setattr(server_manager, "_wait_for_port", lambda port, timeout=30: True)

    class FakeProc:
        pid = 4242

        def poll(self):
            return None

    monkeypatch.setattr(server_manager.subprocess, "Popen", lambda *a, **k: events.append(("launch", a[0])) or FakeProc())
    monkeypatch.setattr(server_manager, "_running_procs", [])
    assert server_manager.start_project_servers() is True
    assert events == [("free", 5174), ("launch", "npm run dev")]
    monkeypatch.setattr(server_manager, "_running_procs", [])
