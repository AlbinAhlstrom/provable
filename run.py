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

os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["PYTHONUTF8"] = "1"

ROOT = os.path.dirname(os.path.abspath(__file__))
IS_WINDOWS = os.name == 'nt'

processes = []

def cleanup(signum=None, frame=None):
    print("\n[provable] Shutting down all services...", flush=True)
    for p in processes:
        if p.poll() is None:
            try:
                if IS_WINDOWS:
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(p.pid)], capture_output=True)
                else:
                    p.terminate()
            except Exception:
                pass
    time.sleep(0.5)
    for p in processes:
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
    p = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        bufsize=1
    )
    processes.append(p)
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

    print("[setup] Verifying and installing Node dependencies...", flush=True)
    node_modules_path = os.path.join(ROOT, "node_modules")
    if not os.path.exists(node_modules_path) or not os.path.exists(os.path.join(node_modules_path, "vite")):
        print("[setup] Running npm install...", flush=True)
        subprocess.run(npm_cmd + ["install"], cwd=ROOT, check=False)

def kill_port_occupants(ports=[8000, 5173]):
    """Terminate any stale processes occupying required application ports on startup."""
    if IS_WINDOWS:
        for port in ports:
            try:
                cmd = f"Get-NetTCPConnection -LocalPort {port} -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess"
                res = subprocess.run(["powershell", "-Command", cmd], capture_output=True, text=True)
                pids = set(res.stdout.strip().split())
                for pid_str in pids:
                    if pid_str.isdigit() and int(pid_str) > 0:
                        subprocess.run(["taskkill", "/F", "/T", "/PID", pid_str], capture_output=True)
            except Exception:
                pass

def wait_for_port(port=8000, timeout=15):
    print(f"[backend] Waiting for backend API to be ready on port {port}...", flush=True)
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection(('localhost', port), timeout=1):
                print(f"[backend] Backend API ready on port {port}!", flush=True)
                return True
        except OSError:
            time.sleep(0.5)
    print(f"[backend] Warning: Backend API port {port} wait timed out.", flush=True)
    return False

def main():
    print(f"=== Provable Application Launcher (OS: {sys.platform}) ===", flush=True)

    # Clean stale port occupants
    kill_port_occupants([8000, 5173])

    # 1. Determine executables & verify host tools
    backend_dir = os.path.join(ROOT, "backend")
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
        npm_cmd = [npm_bin]
    elif shutil.which("npm"):
        npm_cmd = ["npm"]
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

    # 4. Start Development Services
    backend_cmd = [py_exe, "-m", "uvicorn", "main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"]

    print("\n" + "=" * 50, flush=True)
    print("Provable Services Live Links:", flush=True)
    print("  FastAPI Backend API -> http://localhost:8000", flush=True)
    print("  Main Frontend App   -> http://localhost:5173", flush=True)
    print("  Workspace Preview   -> http://localhost:5174", flush=True)
    print("=" * 50 + "\n", flush=True)

    start_process(backend_cmd, cwd=backend_dir, prefix="[backend]")
    wait_for_port(8000, timeout=15)
    start_process(npm_cmd + ["run", "dev"], cwd=ROOT, prefix="[app]    ")

    print("\n[provable] All services running. Press Ctrl+C to stop.\n", flush=True)
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        cleanup()

if __name__ == "__main__":
    main()
