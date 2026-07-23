import pytest


@pytest.mark.api
def test_get_projects(api_client):
    """Test GET /api/projects returns list of projects."""
    response = api_client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.api
def test_get_project_settings(api_client):
    """Test GET /api/project/settings returns active project configuration."""
    response = api_client.get("/api/project/settings")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "dev_server" in data


@pytest.mark.api
def test_add_project(api_client, tmp_path):
    """Test POST /api/projects/add registers a new path."""
    new_proj = tmp_path / "new_project"
    new_proj.mkdir()

    response = api_client.post("/api/projects/add", json={
        "name": "New Test Project",
        "path": str(new_proj)
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
