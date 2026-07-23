import pytest


@pytest.mark.api
def test_get_requirements_empty(api_client):
    """Test GET /api/requirements on a fresh database."""
    response = api_client.get("/api/requirements")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.api
def test_create_and_delete_requirement(api_client):
    """Test POST /api/create-requirement and DELETE /api/requirements/{id}."""
    payload = {
        "title": "API Requirement Test",
        "description": "Created via FastAPI endpoint"
    }

    create_res = api_client.post("/api/create-requirement", json=payload)
    assert create_res.status_code == 200
    created = create_res.json()
    assert created["success"] is True

    # Verify requirement appears in listing
    get_res = api_client.get("/api/requirements")
    assert get_res.status_code == 200
    reqs = get_res.json()
    assert len(reqs) >= 1
    req_id = reqs[0]["id"]

    # Delete requirement
    del_res = api_client.delete(f"/api/requirements/{req_id}")
    assert del_res.status_code == 200

    # Verify requirement is removed
    get_after = api_client.get("/api/requirements")
    req_ids_after = [r["id"] for r in get_after.json()]
    assert req_id not in req_ids_after


@pytest.mark.api
def test_create_folder(api_client):
    """Test POST /api/create-folder creates section folder."""
    response = api_client.post("/api/create-folder", json={
        "title": "Frontend Components"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "FLD-" in data["id"]
