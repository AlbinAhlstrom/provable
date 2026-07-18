import os
import yaml
from typing import List, Dict, Any, Optional

_CONFIG_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'integrations.yaml'))


def _load_config() -> dict:
    if not os.path.exists(_CONFIG_PATH):
        return {}
    with open(_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _save_config(cfg: dict) -> None:
    with open(_CONFIG_PATH, 'w', encoding='utf-8') as f:
        yaml.safe_dump(cfg, f, default_flow_style=False, allow_unicode=True)


def get_workspace_base() -> str:
    """Return the active workspace directory path."""
    # 1. Environment variable override (highest priority — set on project switch)
    env_workspace = os.environ.get("PROVABLE_WORKSPACE")
    if env_workspace:
        return os.path.abspath(env_workspace)

    # 2. integrations.yaml active_project field
    try:
        cfg = _load_config()
        active = cfg.get('active_project') or cfg.get('project', {}).get('workspace_path')
        if active:
            return os.path.abspath(active)
    except Exception as e:
        print(f"⚠️ config_loader: Error reading integrations.yaml: {e}")

    # 3. Fallback default workspace
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace'))


def set_active_project(path: str) -> None:
    """Persist the new active project path to integrations.yaml and env var."""
    path = os.path.abspath(path)
    os.environ["PROVABLE_WORKSPACE"] = path

    cfg = _load_config()
    cfg['active_project'] = path

    # Also update legacy 'project.workspace_path' for backwards compat
    cfg.setdefault('project', {})['workspace_path'] = path

    _save_config(cfg)
    print(f"⚙️ config_loader: Active project set to {path}")


def get_all_projects() -> List[Dict[str, Any]]:
    """Return the list of registered projects from integrations.yaml."""
    cfg = _load_config()
    return cfg.get('projects', [])


def add_project(name: str, path: str) -> None:
    """Register a new project in integrations.yaml if not already listed."""
    path = os.path.abspath(path)
    cfg = _load_config()
    projects = cfg.get('projects', [])

    # Avoid duplicates
    if not any(p['path'] == path for p in projects):
        projects.append({'name': name, 'path': path})
        cfg['projects'] = projects
        _save_config(cfg)
        print(f"⚙️ config_loader: Registered project '{name}' at {path}")


def get_project_settings() -> dict:
    """Return project-specific settings from the active project's .provable.yaml."""
    base = get_workspace_base()

    # Defaults suitable for a Vite/React app (matches old workspace behaviour)
    settings = {
        "name": os.path.basename(base),
        "dev_server": {
            "start_command": "npm run dev",
            "port": 5174,
            "base_url": f"http://localhost:5174"
        },
        "test_runner": {
            "test_command": "pytest -v",
            "framework": "selenium"
        }
    }

    provable_yaml = os.path.join(base, '.provable.yaml')
    if os.path.exists(provable_yaml):
        try:
            with open(provable_yaml, 'r', encoding='utf-8') as f:
                proj_cfg = yaml.safe_load(f)
                if proj_cfg:
                    # Deep-merge so partial .provable.yaml overrides still work
                    for key, val in proj_cfg.items():
                        if isinstance(val, dict) and isinstance(settings.get(key), dict):
                            settings[key].update(val)
                        else:
                            settings[key] = val
        except Exception as e:
            print(f"⚠️ config_loader: Error loading .provable.yaml: {e}")

    return settings
