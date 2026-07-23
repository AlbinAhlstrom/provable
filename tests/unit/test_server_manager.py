import pytest
from onboarding import server_manager


@pytest.mark.unit
def test_get_preview_url():
    """Test get_preview_url returns a valid http string."""
    url = server_manager.get_preview_url()
    assert isinstance(url, str)
    assert url.startswith("http")


@pytest.mark.unit
def test_get_server_status():
    """Test get_server_status returns valid status structure."""
    status = server_manager.get_server_status()
    assert isinstance(status, dict)
    assert "running" in status
    assert "processes" in status
    assert "preview_url" in status


@pytest.mark.unit
def test_stop_project_servers():
    """Test stop_project_servers safely terminates any stored processes."""
    server_manager.stop_project_servers()
    status = server_manager.get_server_status()
    assert status["running"] is False
    assert len(status["processes"]) == 0
