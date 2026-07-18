"""
Workspace Discovery Agent — inspects a project folder and auto-generates
a .provable.yaml with the correct start commands, ports, and test runner config.
"""
import os
import sys
import re
import yaml
from typing import Dict, Any

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agent_orchestrator import call_gemini


def _read_file_safe(path: str, max_bytes: int = 4096) -> str:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read(max_bytes)
    except Exception:
        return ""


def discover_project_config(project_path: str) -> Dict[str, Any]:
    """
    Analyse a project folder and return a .provable.yaml config dict.
    Falls back to sensible defaults if discovery is inconclusive.
    """
    project_path = os.path.abspath(project_path)
    clues = {}

    # --- Collect evidence ---
    # package.json
    pkg_json = os.path.join(project_path, 'package.json')
    if os.path.exists(pkg_json):
        clues['package.json'] = _read_file_safe(pkg_json)

    # pyproject.toml / requirements.txt
    for f in ['pyproject.toml', 'requirements.txt', 'setup.py']:
        fp = os.path.join(project_path, f)
        if os.path.exists(fp):
            clues[f] = _read_file_safe(fp)

    # Start scripts
    for f in ['dev.sh', 'start.sh', 'Makefile', 'docker-compose.yml', 'docker-compose.yaml']:
        fp = os.path.join(project_path, f)
        if os.path.exists(fp):
            clues[f] = _read_file_safe(fp)

    # README for running instructions
    for readme in ['README.md', 'README.rst', 'README']:
        fp = os.path.join(project_path, readme)
        if os.path.exists(fp):
            clues[readme] = _read_file_safe(fp, max_bytes=3000)
            break

    # Top-level directory listing for context
    top_dirs = [d for d in os.listdir(project_path)
                if os.path.isdir(os.path.join(project_path, d)) and not d.startswith('.')]
    clues['directories'] = ', '.join(top_dirs)

    # Detect test framework
    test_framework = 'pytest'
    e2e_dir = os.path.join(project_path, 'tests', 'e2e')
    if os.path.exists(e2e_dir):
        conftest = _read_file_safe(os.path.join(e2e_dir, 'conftest.py'))
        if 'playwright' in conftest.lower():
            test_framework = 'playwright'
        elif 'selenium' in conftest.lower():
            test_framework = 'selenium'

    # --- Ask LLM ---
    evidence_text = "\n\n".join([f"=== {name} ===\n{content}" for name, content in clues.items()])

    prompt = f"""
You are an expert DevOps engineer. Analyse the following project files and generate a .provable.yaml configuration.

PROJECT: {os.path.basename(project_path)}
DETECTED TEST FRAMEWORK: {test_framework}

PROJECT FILES:
{evidence_text}

Return ONLY a valid YAML block with this exact structure (no markdown, no explanations):

name: <project name>
dev_server:
  start_command: <shell command OR list of shell commands to start all required servers>
  port: <primary frontend port number as integer>
  base_url: "http://localhost:<port>"
test_runner:
  test_command: <pytest command including correct test directory>
  framework: <pytest|playwright|selenium>

Rules:
- start_command can be a list if multiple processes are needed (e.g. backend + frontend)
- All commands must be runnable from the project root directory
- Use the venv if a Python venv is detected (e.g. 'source venv/bin/activate && uvicorn ...')
- The port must be the frontend/UI port that will be embedded in a preview iframe
"""

    print(f"🔍 workspace_discovery: Analysing {os.path.basename(project_path)} with LLM...")
    raw = call_gemini(prompt)

    # Strip markdown fences if present
    raw = re.sub(r'^```[a-zA-Z]*\n?', '', raw.strip())
    raw = re.sub(r'\n?```$', '', raw.strip())

    try:
        config = yaml.safe_load(raw)
        if not isinstance(config, dict):
            raise ValueError("LLM did not return a dict")
    except Exception as e:
        print(f"⚠️ workspace_discovery: Could not parse LLM response ({e}), using defaults")
        config = {}

    # Merge with safe defaults
    defaults = {
        "name": os.path.basename(project_path),
        "dev_server": {
            "start_command": "npm start",
            "port": 3000,
            "base_url": "http://localhost:3000"
        },
        "test_runner": {
            "test_command": f"pytest tests/",
            "framework": test_framework
        }
    }
    for key, val in defaults.items():
        if key not in config:
            config[key] = val
        elif isinstance(val, dict) and isinstance(config.get(key), dict):
            for subkey, subval in val.items():
                config[key].setdefault(subkey, subval)

    return config


def write_provable_yaml(project_path: str, config: Dict[str, Any]) -> str:
    """Write a .provable.yaml to the project root and return the path."""
    out_path = os.path.join(project_path, '.provable.yaml')
    with open(out_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(config, f, default_flow_style=False, allow_unicode=True)
    print(f"📝 workspace_discovery: Written .provable.yaml to {out_path}")
    return out_path
