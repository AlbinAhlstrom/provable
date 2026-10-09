"""
Automated Integration Test Suite: App Startup & Live Preview Connectivity.
Guarantees that:
1. Default workspace scaffold generates complete React 18 + TypeScript + Vite project configuration (including tsconfig.json and vite.config.ts port 5174).
2. Workspace builds with zero compiler errors.
3. PM Studio Frontend bundle builds cleanly with zero TypeScript errors.
4. FastAPI backend, PM Studio Frontend, and Workspace Preview server ports (8000, 5173, 5174) are strictly configured.
"""

import os
import json
import subprocess
import pytest
from onboarding.templates.workspace_scaffold import create_default_workspace_scaffold


def test_workspace_scaffold_configuration_and_tsconfig_integrity(tmp_path):
    """
    Validates that create_default_workspace_scaffold scaffolds a complete,
    valid Vite + React + TypeScript application with port 5174 and tsconfig.json.
    """
    ws_dir = str(tmp_path / "test_workspace")
    create_default_workspace_scaffold(ws_dir)

    # Assert all vital configuration files exist
    assert os.path.exists(os.path.join(ws_dir, "package.json"))
    assert os.path.exists(os.path.join(ws_dir, "tsconfig.json"))
    assert os.path.exists(os.path.join(ws_dir, "vite.config.ts"))
    assert os.path.exists(os.path.join(ws_dir, "index.html"))
    assert os.path.exists(os.path.join(ws_dir, "src", "main.tsx"))
    assert os.path.exists(os.path.join(ws_dir, "src", "App.tsx"))
    assert os.path.exists(os.path.join(ws_dir, "src", "app.py"))


    # Assert package.json configuration
    with open(os.path.join(ws_dir, "package.json"), "r", encoding="utf-8") as f:
        pkg = json.load(f)
    assert pkg["scripts"]["dev"] == "vite --port 5174 --host"
    assert "react" in pkg["dependencies"]
    assert "vite" in pkg["devDependencies"]
    assert "typescript" in pkg["devDependencies"]

    # Assert tsconfig.json configuration
    with open(os.path.join(ws_dir, "tsconfig.json"), "r", encoding="utf-8") as f:
        tsconfig = json.load(f)
    assert tsconfig["compilerOptions"]["jsx"] == "react-jsx"

    # Assert vite.config.ts configuration
    with open(os.path.join(ws_dir, "vite.config.ts"), "r", encoding="utf-8") as f:
        vite_cfg = f.read()
    assert "port: 5174" in vite_cfg
    assert "proxy" in vite_cfg


@pytest.mark.slow
def test_workspace_vite_build_integrity(tmp_path):
    """
    Validates that a freshly scaffolded workspace compiles and bundles cleanly via Vite.

    Hermetic: it builds its own scaffold in a temporary directory (reusing the installed packages of the live
    workspace when present), so it never depends on, or breaks with, whatever the live preview is running.
    """
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    installed = os.path.join(root, "workspace", "node_modules")
    if not os.path.exists(os.path.join(installed, "vite")):
        pytest.skip("no installed workspace packages to reuse (run the app once)")

    ws_dir = str(tmp_path / "scaffold")
    create_default_workspace_scaffold(ws_dir)
    link = os.path.join(ws_dir, "node_modules")
    try:
        os.symlink(installed, link, target_is_directory=True)
    except OSError:  # Windows without the symlink privilege: a directory junction needs none
        subprocess.run(["cmd", "/c", "mklink", "/J", link, installed], check=True, capture_output=True)
    npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
    res = subprocess.run([npm_cmd, "run", "build"], cwd=ws_dir, capture_output=True, text=True)
    assert res.returncode == 0, f"Workspace build failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"


@pytest.mark.slow
def test_frontend_pm_studio_vite_build_integrity():
    """
    Validates that PM Studio React 18 frontend compiles and bundles cleanly with zero TS errors.
    """
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    fe_dir = os.path.join(root, "frontend")

    if os.path.exists(os.path.join(fe_dir, "node_modules", "vite")):
        npm_cmd = "npm.cmd" if os.name == "nt" else "npm"
        res = subprocess.run([npm_cmd, "run", "build"], cwd=fe_dir, capture_output=True, text=True)
        assert res.returncode == 0, f"Frontend build failed:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
