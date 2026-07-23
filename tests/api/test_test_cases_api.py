import pytest


@pytest.mark.api
def test_get_coverage_api(api_client):
    """Test GET /api/coverage endpoint returns metrics."""
    response = api_client.get("/api/coverage")
    assert response.status_code == 200
    data = response.json()
    assert "summary" in data
    assert "total_requirements" in data["summary"]
    assert "passing" in data["summary"]
    assert "failing" in data["summary"]
    assert "uncovered" in data["summary"]
