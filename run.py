#!/usr/bin/env python3
"""
run.py — Single unified script for running Provable on Windows host or Linux/WSL.
Handles environment detection, automatic dependency installation/upgrades, Docker container startup, and process management.
"""

import sys
import os
import shutil
import subprocess
import threading
import signal
import time
import socket

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

ROOT = os.path.dirname(os.path.abspath(__file__))
IS_WINDOWS = os.name == 'nt'

processes = []

def cleanup(signum=None, frame=None):
    print("\n[provable] Shutting down all services...", flush=True)
    for tuple_item in processes:
        p = tuple_item[0]
        if p.poll() is None:
            try:
                if IS_WINDOWS:
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
                else:
                    p.terminate()
            except Exception:
                pass
    time.sleep(0.5)
    for tuple_item in processes:
        p = tuple_item[0]
        if p.poll() is None:
            try:
                p.kill()
            except Exception:
                pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup)
signal.signal(signal.SIGTERM, cleanup)

def log_stream(stream, prefix):
    for line in iter(stream.readline, ''):
        if line:
            print(f"{prefix} {line.rstrip()}", flush=True)

def start_process(cmd, cwd, prefix):
    print(f"{prefix} Starting: {' '.join(cmd)} (in {cwd})", flush=True)
    kwargs = {
        "cwd": cwd,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "encoding": "utf-8",
        "errors": "replace",
        "bufsize": 1
    }
    if IS_WINDOWS and hasattr(subprocess, "CREATE_NEW_PROCESS_GROUP"):
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

    p = subprocess.Popen(cmd, **kwargs)
    processes.append((p, cmd, cwd, prefix))
    t = threading.Thread(target=log_stream, args=(p.stdout, prefix), daemon=True)
    t.start()
    return p

def auto_setup_environment(py_exe, npm_cmd):
    print("[setup] Verifying and installing Python dependencies...", flush=True)
    required_pkgs = [
        "fastapi>=0.100.0",
        "uvicorn>=0.23.0",
        "pydantic>=2.0.0",
        "langgraph>=0.2.0",
        "openai>=1.0.0",
        "sqlalchemy",
        "aiosqlite",
        "requests",
        "pytest",
        "selenium",
        "python-dotenv",
        "pyyaml"
    ]
    # Install/upgrade required python packages automatically
    subprocess.run([py_exe, "-m", "pip", "install", "--upgrade"] + required_pkgs, check=False)

    print("[setup] Verifying and installing Node dependencies for PM Studio frontend...", flush=True)
    frontend_dir = os.path.join(ROOT, "frontend")
    node_modules_path = os.path.join(frontend_dir, "node_modules")
    if not os.path.exists(node_modules_path) or not os.path.exists(os.path.join(node_modules_path, "vite")):
        print("[setup] Running npm install in frontend/...", flush=True)
        subprocess.run(npm_cmd + ["install"], cwd=frontend_dir, check=False)

def kill_port_occupants(ports=[8000, 5173, 5174]):
    """Terminate any stale processes occupying required application ports on startup."""
    current_pid = os.getpid()
    for port in ports:
        try:
            if IS_WINDOWS:
                res = subprocess.run(f"netstat -ano | findstr :{port}", shell=True, capture_output=True, text=True)
                if res.stdout:
                    for line in res.stdout.strip().splitlines():
                        parts = line.split()
                        if len(parts) >= 5 and "LISTENING" in line:
                            pid = parts[-1]
                            if pid != "0" and int(pid) != current_pid:
                                subprocess.run(f"taskkill /F /T /PID {pid}", shell=True, capture_output=True)
            else:
                subprocess.run(f"fuser -k -9 {port}/tcp", shell=True, capture_output=True)
        except Exception as e:
            print(f"[setup] Port {port} cleanup notice: {e}", flush=True)

def is_port_in_use(port: int) -> bool:
    try:
        with socket.create_connection(('localhost', port), timeout=0.5):
            return True
    except OSError:
        return False


def wait_for_port(port=8000, timeout=15):
    print(f"[backend] Waiting for backend API to be ready on port {port}...", flush=True)
    start = time.time()
    while time.time() - start < timeout:
        if is_port_in_use(port):
            print(f"[backend] Backend API ready on port {port}!", flush=True)
            return True
        time.sleep(0.5)
    print(f"[backend] Warning: Backend API port {port} wait timed out.", flush=True)
    return False


def main():
    print(f"=== Provable Application Launcher (OS: {sys.platform}) ===", flush=True)

    # Clean stale port occupants
    kill_port_occupants([8000, 5173, 5174])

    # 1. Determine executables & verify host tools
    backend_dir = os.path.join(ROOT, "backend")
    frontend_dir = os.path.join(ROOT, "frontend")
    venv_py = os.path.join(
        backend_dir,
        "venv",
        "Scripts" if IS_WINDOWS else "bin",
        "python.exe" if IS_WINDOWS else "python"
    )
    if os.path.exists(venv_py):
        py_exe = venv_py
    else:
        py_exe = sys.executable

    # Check for npm
    npm_bin = shutil.which("npm.cmd") if IS_WINDOWS else shutil.which("npm")
    if npm_bin:
        npm_cmd = ["cmd.exe", "/c", npm_bin] if IS_WINDOWS else [npm_bin]
    elif shutil.which("npm"):
        npm_cmd = ["cmd.exe", "/c", "npm"] if IS_WINDOWS else ["npm"]
    elif IS_WINDOWS and shutil.which("wsl"):
        npm_cmd = ["wsl", "npm"]
    else:
        print("\n[ERROR] Node.js / npm is not installed or not found in system PATH.", flush=True)
        print("Please install Node.js from https://nodejs.org/ or via 'winget install OpenJS.NodeJS.LTS'", flush=True)
        sys.exit(1)

    # Check for Docker
    docker_bin = shutil.which("docker")
    if not docker_bin:
        print("\n[WARNING] Docker is not installed or not in PATH.", flush=True)
        print("Install Docker Desktop from https://www.docker.com/products/docker-desktop to run Allure dashboard.", flush=True)

    # 2. Automated Dependency Setup
    auto_setup_environment(py_exe, npm_cmd)

    # 3. Start Allure Dashboard Docker Container
    print("\n[allure] Starting Allure Dashboard container...", flush=True)
    try:
        res = subprocess.run(
            ["docker", "compose", "-f", "docker-compose.allure.yaml", "up", "-d"],
            cwd=ROOT,
            capture_output=True,
            text=True
        )
        if res.returncode != 0 and "Conflict" in res.stderr:
            subprocess.run(["docker", "rm", "-f", "allure-service"], cwd=ROOT, capture_output=True)
            subprocess.run(["docker", "compose", "-f", "docker-compose.allure.yaml", "up", "-d"], cwd=ROOT, capture_output=True)
        print("[allure] Container running on http://localhost:5050", flush=True)
    except Exception as e:
        print(f"[allure] Docker notification: {e}", flush=True)

    # 4. Start Development Services (Scoped reload to backend/ directory, excluding log/db files)
    run_server_script = os.path.join(backend_dir, "run_server.py")
    backend_cmd = [
        py_exe, run_server_script, "main:app",
        "--reload",
        "--reload-dir", backend_dir,
        "--reload-exclude", "*.log",
        "--reload-exclude", "*.db",
        "--reload-exclude", "*.sdoc",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]

    print("\n" + "=" * 50, flush=True)
    print("Provable Services Live Links:", flush=True)
    print("  FastAPI Backend API -> http://localhost:8000", flush=True)
    print("  Main Frontend App   -> http://localhost:5173", flush=True)
    print("  Workspace Preview   -> http://localhost:5174", flush=True)
    print("=" * 50 + "\n", flush=True)

    start_process(backend_cmd, cwd=backend_dir, prefix="[backend]")
    wait_for_port(8000, timeout=30)
    start_process(npm_cmd + ["run", "dev"], cwd=frontend_dir, prefix="[app]    ")

    ws_dir = os.path.join(ROOT, "workspace")
    if os.path.exists(os.path.join(ws_dir, "package.json")):
        # Ensure node_modules exists in workspace if needed
        if not os.path.exists(os.path.join(ws_dir, "node_modules")):
            print("[preview] Running npm install in workspace...", flush=True)
            subprocess.run(npm_cmd + ["install"], cwd=ws_dir, check=False)
        if not is_port_in_use(5174):
            print("[preview] Starting Workspace Preview Vite dev server on port 5174...", flush=True)
            start_process(npm_cmd + ["run", "dev"], cwd=ws_dir, prefix="[preview]")
        else:
            print("[preview] Workspace Preview active on port 5174 (managed by backend server manager).", flush=True)


    print("\n[provable] All services running continuously with auto-recovery enabled. Press Ctrl+C to stop.\n", flush=True)
    try:
        while True:
            time.sleep(2)
            # Monitor background processes for unexpected exits and auto-restart if needed
            for tuple_item in list(processes):
                p, cmd, cwd, prefix = tuple_item
                if p.poll() is not None:
                    print(f"⚠️ [provable] Service process {prefix.strip()} (PID {p.pid}) exited with code {p.poll()}. Auto-restarting in 1s...", flush=True)
                    processes.remove(tuple_item)
                    time.sleep(1)
                    start_process(cmd, cwd, prefix)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
