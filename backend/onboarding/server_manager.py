"""
Server Manager — lifecycle management for per-project dev server processes.
Reads launch configuration from a project's .provable.yaml and manages PIDs.
"""
import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='backslashreplace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='backslashreplace')

import subprocess
import time
import socket
import signal
from typing import Optional, List

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config_loader import get_project_settings, get_workspace_base

# Tracks running server subprocesses
_running_procs: List[subprocess.Popen] = []


def _wait_for_port(port: int, timeout: int = 30) -> bool:
    """Poll until a TCP port is open or timeout is reached."""
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(('localhost', port), timeout=1):
                return True
        except OSError:
            time.sleep(0.5)
    return False


def _kill_pid_tree(pid: int) -> None:
    """Kill a process and everything it started. `npm run dev` is a shell -> npm -> node chain; terminating only the
    shell (all that Popen.terminate() does on Windows) leaves the node dev server running."""
    if sys.platform == "win32":
        subprocess.run(["taskkill", "/F", "/T", "/PID", str(pid)], capture_output=True)
        return
    try:
        os.killpg(os.getpgid(pid), signal.SIGKILL)
    except (ProcessLookupError, PermissionError, OSError):
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass


def _terminate_tree(proc: subprocess.Popen) -> None:
    _kill_pid_tree(proc.pid)
    try:
        proc.wait(timeout=5)
    except Exception:
        pass


def _listening_pids(netstat_output: str, port: int) -> List[int]:
    """PIDs listening on exactly `port`, from `netstat -ano` output."""
    pids: List[int] = []
    for line in netstat_output.splitlines():
        parts = line.split()
        if len(parts) >= 5 and parts[3] == "LISTENING" and parts[1].rsplit(":", 1)[-1] == str(port):
            pid = int(parts[-1])
            if pid > 0 and pid not in pids:
                pids.append(pid)
    return pids


def free_port(port: int) -> None:
    """Kill whatever listens on `port` (with its children), like the launcher does for the application ports. A backend
    that hot-reloads loses its in-memory process list, so the port itself is the only reliable handle on the previous
    dev server."""
    try:
        if sys.platform == "win32":
            out = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True).stdout
            pids = _listening_pids(out, port)
        else:
            out = subprocess.run(["lsof", "-t", f"-iTCP:{port}", "-sTCP:LISTEN"], capture_output=True, text=True).stdout
            pids = [int(p) for p in out.split()]
        for pid in pids:
            if pid != os.getpid():
                _kill_pid_tree(pid)
                print(f"🛑 server_manager: Freed port {port} (stopped PID {pid} and its children)", flush=True)
    except Exception as e:
        print(f"⚠️ server_manager: Could not free port {port}: {e}", flush=True)


def stop_project_servers() -> None:
    """Terminate all running project dev-server processes, including their child processes."""
    global _running_procs
    for proc in _running_procs:
        try:
            if proc.poll() is None:
                _terminate_tree(proc)
            print(f"🛑 server_manager: Stopped process PID {proc.pid}")
        except Exception as e:
            print(f"⚠️ server_manager: Error stopping process: {e}")
    _running_procs = []


def start_project_servers(project_path: Optional[str] = None) -> bool:
    """
    Start the dev server(s) for the active project.
    Reads config from [project_path]/.provable.yaml.
    Returns True if the server came up successfully.
    """
    global _running_procs
    stop_project_servers()

    base = project_path or get_workspace_base()
    settings = get_project_settings()
    dev_cfg = settings.get('dev_server', {})

    if not dev_cfg.get('enabled', True):
        print(f"ℹ️ server_manager: Dev server disabled for {os.path.basename(base)}")
        return False

    start_cmd = dev_cfg.get('start_command', '')
    if not start_cmd:
        print(f"ℹ️ server_manager: No start_command defined for {os.path.basename(base)}")
        return False

    port = int(dev_cfg.get('port') or 5174)
    free_port(port)  # a previous backend process (hot reload) may still hold it; never stack a second server beside it

    # Support multi-process launch (e.g. backend + frontend microservices)
    # If start_command is a list, launch each sequentially
    commands = start_cmd if isinstance(start_cmd, list) else [start_cmd]

    print(f"🚀 server_manager: Starting dev server(s) for {os.path.basename(base)}...")

    for cmd in commands:
        cmd_has_pkg = (
            os.path.exists(os.path.join(base, 'package.json')) or
            any(os.path.exists(os.path.join(base, sub, 'package.json')) for sub in ['frontend', 'client', 'app', 'ui', 'web'])
        )

        if ('npm' in cmd or 'npx' in cmd) and not cmd_has_pkg:
            print(f"⚠️ server_manager: Skipping '{cmd}' — package.json not found in {base} or subfolders")
            continue

        log_path = os.path.join(base, "dev_server.log")
        try:
            log_file = open(log_path, "a", encoding="utf-8")
            proc = subprocess.Popen(
                cmd,
                shell=True,
                cwd=base,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                start_new_session=True
            )
            _running_procs.append(proc)
            print(f"  ▶ PID {proc.pid}: {cmd} (logging to {log_path})", flush=True)
        except Exception as e:
            print(f"❌ server_manager: Failed to start '{cmd}': {e}", flush=True)
            return False

    if not _running_procs:
        print(f"ℹ️ server_manager: No processes launched for {os.path.basename(base)}", flush=True)
        return False

    # Wait for the primary frontend port to come up
    print(f"  ⏳ Waiting for port {port}...", flush=True)
    if _wait_for_port(port, timeout=45):
        print(f"✅ server_manager: Server ready on port {port}", flush=True)
        return True
    else:
        print(f"⚠️ server_manager: Timed out waiting for port {port} — server may still be starting", flush=True)
        if os.path.exists(log_path):
            try:
                with open(log_path, "r", encoding="utf-8", errors="replace") as lf:
                    lines = lf.readlines()
                    if lines:
                        print(f"  📜 Recent output from {log_path}:\n{''.join(lines[-15:])}", flush=True)
            except Exception:
                pass
        return False


def get_preview_url() -> str:
    """Return the base URL for the active project's frontend."""
    settings = get_project_settings()
    return settings.get('dev_server', {}).get('base_url', 'http://localhost:5174')


def get_server_status() -> dict:
    """Return current status of managed server processes."""
    statuses = []
    for proc in _running_procs:
        statuses.append({
            "pid": proc.pid,
            "running": proc.poll() is None
        })
    return {
        "running": any(s["running"] for s in statuses),
        "processes": statuses,
        "preview_url": get_preview_url()
    }
