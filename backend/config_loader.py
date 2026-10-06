import os
import sys
import yaml
from typing import List, Dict, Any, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(line_buffering=True, encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(line_buffering=True, encoding="utf-8")
    except Exception:
        pass

def _get_config_path() -> str:
    return os.environ.get(
        "PROVABLE_CONFIG_PATH",
        os.path.abspath(os.path.join(os.path.dirname(__file__), 'config', 'integrations.yaml'))
    )


def _load_config() -> dict:
    cfg_path = _get_config_path()
    if not os.path.exists(cfg_path):
        return {}
    with open(cfg_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def _save_config(cfg: dict) -> None:
    cfg_path = _get_config_path()
    os.makedirs(os.path.dirname(cfg_path), exist_ok=True)
    with open(cfg_path, 'w', encoding='utf-8') as f:
        yaml.safe_dump(cfg, f, default_flow_style=False, allow_unicode=True)


def get_workspace_base() -> str:
    """Return the active workspace directory path."""
    # 1. Environment variable override (highest priority — set on project switch)
    env_workspace = os.environ.get("PROVABLE_WORKSPACE")
    if env_workspace and os.path.exists(env_workspace):
        return os.path.abspath(env_workspace)

    # 2. integrations.yaml active_project field
    try:
        cfg = _load_config()
        active = cfg.get('active_project') or cfg.get('project', {}).get('workspace_path')
        if active and os.path.exists(active):
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
    projects = cfg.get('projects', [])

    # Ensure default workspace project is always present in the list
    default_ws = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'workspace'))
    if not any(os.path.normcase(os.path.abspath(p.get('path', ''))) == os.path.normcase(default_ws) for p in projects):
        projects.insert(0, {'name': 'Default Workspace', 'path': default_ws})

    return projects


def add_project(name: str, path: str) -> None:
    """Register a new project in integrations.yaml if not already listed."""
    path = os.path.abspath(path)
    cfg = _load_config()
    projects = cfg.get('projects', [])

    # Avoid duplicates
    if not any(os.path.normcase(os.path.abspath(p['path'])) == os.path.normcase(path) for p in projects):
        projects.append({'name': name, 'path': path})
        cfg['projects'] = projects
        _save_config(cfg)
        print(f"⚙️ config_loader: Registered project '{name}' at {path}")


def get_project_settings() -> dict:
    """Return project-specific settings from the active project's .provable.yaml."""
    base = get_workspace_base()

    # Find name from registered projects if matched
    proj_name = os.path.basename(base)
    norm_base = os.path.normcase(os.path.abspath(base))
    for p in get_all_projects():
        if os.path.normcase(os.path.abspath(p.get('path', ''))) == norm_base:
            proj_name = p.get('name', proj_name)
            break

    has_pkg_json = (
        os.path.exists(os.path.join(base, 'package.json')) or
        any(os.path.exists(os.path.join(base, sub, 'package.json')) for sub in ['frontend', 'client', 'app', 'ui', 'web'])
    )
    provable_yaml = os.path.join(base, '.provable.yaml')
    has_provable_yaml = os.path.exists(provable_yaml)

    # Only default dev_server to enabled if package.json or .provable.yaml exists
    has_dev_server = has_pkg_json or has_provable_yaml

    settings = {
        "name": proj_name,
        "dev_server": {
            "enabled": has_dev_server,
            "start_command": "npm run dev" if has_pkg_json else "",
            "port": 5174 if has_dev_server else None,
            "base_url": "http://localhost:5174"
        },
        "test_runner": {
            "test_command": "pytest -v",
            "framework": "selenium"
        }
    }

    if has_provable_yaml:
        try:
            with open(provable_yaml, 'r', encoding='utf-8') as f:
                proj_cfg = yaml.safe_load(f)
                if proj_cfg:
                    for key, val in proj_cfg.items():
                        if isinstance(val, dict) and isinstance(settings.get(key), dict):
                            settings[key].update(val)
                        else:
                            settings[key] = val
                    if 'dev_server' in proj_cfg:
                        settings['dev_server']['enabled'] = True
        except Exception as e:
            print(f"⚠️ config_loader: Error loading .provable.yaml: {e}")

    return settings
