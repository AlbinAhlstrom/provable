import os
import pytest
import config_loader


@pytest.mark.unit
def test_get_workspace_base_env_override(tmp_path, monkeypatch):
    """Test get_workspace_base when environment variable PROVABLE_WORKSPACE is set."""
    fake_ws = tmp_path / "fake_workspace"
    fake_ws.mkdir()
    monkeypatch.setenv("PROVABLE_WORKSPACE", str(fake_ws))

    base = config_loader.get_workspace_base()
    assert base == str(fake_ws)


@pytest.mark.unit
def test_get_all_projects():
    """Test get_all_projects returns a list containing at least default projects."""
    projects = config_loader.get_all_projects()
    assert isinstance(projects, list)
    assert len(projects) >= 1
    # Check each entry has name and path
    for p in projects:
        assert "name" in p
        assert "path" in p


@pytest.mark.unit
def test_get_project_settings(tmp_path, monkeypatch):
    """Test get_project_settings returns valid dictionary layout."""
    fake_ws = tmp_path / "my_project"
    fake_ws.mkdir()
    monkeypatch.setenv("PROVABLE_WORKSPACE", str(fake_ws))

    settings = config_loader.get_project_settings()
    assert "name" in settings
    assert "dev_server" in settings
    assert "test_runner" in settings
    assert settings["name"] == "my_project"
