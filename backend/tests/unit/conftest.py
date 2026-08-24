import pytest

@pytest.fixture(autouse=True)
def mock_allure_client_network_calls(monkeypatch):
    """
    Autouse fixture ensuring unit tests never block on external network I/O or timeouts.
    """
    try:
        from integrations import allure_client
        monkeypatch.setattr(
            allure_client,
            "load_allure_config",
            lambda: {"enabled": False, "server_url": "http://localhost:5050", "project_id": "default"}
        )
        monkeypatch.setattr(allure_client, "trigger_allure_generation", lambda: None)
    except ImportError:
        pass
