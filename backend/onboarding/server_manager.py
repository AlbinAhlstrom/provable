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


def stop_project_servers() -> None:
    """Terminate all running project dev-server processes."""
    global _running_procs
    for proc in _running_procs:
        try:
            if proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
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

    # Support multi-process launch (e.g. backend + frontend for v-chess)
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

        try:
            proc = subprocess.Popen(
                cmd,
                shell=True,
                cwd=base,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True
            )
            _running_procs.append(proc)
            print(f"  ▶ PID {proc.pid}: {cmd}")
        except Exception as e:
            print(f"❌ server_manager: Failed to start '{cmd}': {e}")
            return False

    if not _running_procs:
        print(f"ℹ️ server_manager: No processes launched for {os.path.basename(base)}")
        return False

    # Wait for the primary frontend port to come up
    print(f"  ⏳ Waiting for port {port}...")
    if _wait_for_port(port, timeout=45):
        print(f"✅ server_manager: Server ready on port {port}")
        return True
    else:
        print(f"⚠️ server_manager: Timed out waiting for port {port} — server may still be starting")
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
