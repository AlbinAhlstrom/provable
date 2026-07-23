import os
import pytest
from onboarding import workspace_discovery_agent


@pytest.mark.system
def test_discover_project_config_defaults(tmp_path, monkeypatch):
    """Test project configuration discovery fallback on an empty directory using mock LLM."""
    mock_yaml = """
name: empty_project
dev_server:
  start_command: npm run dev
  port: 5173
  base_url: "http://localhost:5173"
test_runner:
  test_command: pytest tests/
  framework: pytest
"""
    monkeypatch.setattr(workspace_discovery_agent, "call_gemini", lambda prompt: mock_yaml)

    empty_proj = tmp_path / "empty_project"
    empty_proj.mkdir()

    cfg = workspace_discovery_agent.discover_project_config(str(empty_proj))
    assert isinstance(cfg, dict)
    assert "dev_server" in cfg
    assert "test_runner" in cfg
    assert cfg["name"] == "empty_project"
    assert cfg["dev_server"]["port"] == 5173


@pytest.mark.system
def test_write_provable_yaml(tmp_path):
    """Test writing discovered config to .provable.yaml."""
    proj = tmp_path / "node_proj"
    proj.mkdir()

    cfg = {
        "name": "Node Proj",
        "dev_server": {"start_command": "npm run dev", "port": 5173, "base_url": "http://localhost:5173"},
        "test_runner": {"test_command": "pytest tests/", "framework": "pytest"}
    }

    yaml_path = workspace_discovery_agent.write_provable_yaml(str(proj), cfg)
    assert os.path.exists(yaml_path)
    assert os.path.basename(yaml_path) == ".provable.yaml"
