import pytest


@pytest.mark.api
def test_get_agent_status(api_client):
    """Test GET /api/agent-status returns execution state."""
    response = api_client.get("/api/agent-status")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "backlog_analysis" in data


@pytest.mark.api
def test_get_reviews_empty(api_client):
    """Test GET /api/reviews returns empty review list when no agents are in review."""
    response = api_client.get("/api/reviews")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
